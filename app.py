"""
Personal AI Assistant with RAG and Function Calling
Combines vector database retrieval with OpenAI function calling
"""

import os
import glob
import json
import requests
import warnings
from dotenv import load_dotenv
import gradio as gr
from pypdf import PdfReader
import numpy as np
from pydantic import BaseModel

# Suppress LangChain chunk size warnings
warnings.filterwarnings('ignore', message='Created a chunk of size.*')

# LangChain imports for RAG
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

# OpenAI imports for function calling
from openai import OpenAI


# Configuration
MODEL = "gpt-4o-mini"
EVALUATOR_MODEL = "gemini-2.0-flash-exp"
DB_NAME = "vector_db"
KNOWLEDGE_BASE_PATH = "Knowledge_Base"
PDF_PATH = "me/linkedin.pdf"
SUMMARY_PATH = "me/summary.txt"

# Performance settings
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
TOP_K_RETRIEVAL = 3
MAX_CONTEXT_LENGTH = 3000


# Pydantic model for evaluation
class Evaluation(BaseModel):
    is_acceptable: bool
    feedback: str


# Load environment variables
load_dotenv(override=True)

# Check for OpenAI API key
openai_api_key = os.getenv('OPENAI_API_KEY')
if not openai_api_key:
    raise ValueError(
        "OPENAI_API_KEY not found! Please set it as an environment variable or secret in HuggingFace Spaces.\n"
        "Go to Settings > Repository Secrets and add OPENAI_API_KEY with your API key."
    )
os.environ['OPENAI_API_KEY'] = openai_api_key

# Initialize Gemini for evaluation (optional)
google_api_key = os.getenv('GOOGLE_API_KEY')
if google_api_key:
    gemini = OpenAI(
        api_key=google_api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    print("✓ Gemini evaluator enabled")
else:
    gemini = None
    print("ℹ Gemini evaluator not configured (optional - responses will not be evaluated)")


def push(text):
    """Send push notification via Pushover"""
    print(f"📱 Push: {text}")
    pushover_user = os.getenv("PUSHOVER_USER")
    pushover_token = os.getenv("PUSHOVER_TOKEN")
    
    if pushover_user and pushover_token:
        try:
            requests.post(
                "https://api.pushover.net/1/messages.json",
                data={
                    "token": pushover_token,
                    "user": pushover_user,
                    "message": text,
                }
            )
        except Exception as e:
            print(f"Warning: Could not send push notification: {e}")


def record_user_details(email, name="Name not provided", notes="not provided"):
    """Record user contact information and interest"""
    push(f"Recording interest from {name} with email {email} and notes {notes}")
    return {"recorded": "ok", "message": "Thank you! I've recorded your details and will be in touch."}


def record_unknown_question(question):
    """Record questions that couldn't be answered"""
    push(f"Recording unknown question: {question}")
    return {"recorded": "ok", "message": "I've noted this question for follow-up."}


# Tool schemas for OpenAI function calling
record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "The email address of this user"
            },
            "name": {
                "type": "string",
                "description": "The user's name, if they provided it"
            },
            "notes": {
                "type": "string",
                "description": "Any additional information about the conversation that's worth recording to give context"
            }
        },
        "required": ["email"],
        "additionalProperties": False
    }
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that couldn't be answered"
            }
        },
        "required": ["question"],
        "additionalProperties": False
    }
}

tools = [
    {"type": "function", "function": record_user_details_json},
    {"type": "function", "function": record_unknown_question_json}
]


class PersonalAI:
    """Personal AI Assistant with RAG and Function Calling"""

    def __init__(self):
        self.openai = OpenAI()
        self.name = "Hoang Nhat Duy Le"
        
        # Load LinkedIn profile
        reader = PdfReader(PDF_PATH)
        self.linkedin = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                self.linkedin += text
        
        # Load summary
        with open(SUMMARY_PATH, "r", encoding="utf-8") as f:
            self.summary = f.read()
        
        # Initialize RAG components
        self._initialize_rag()
        
        print(f"✓ Personal AI initialized for: {self.name}")
        print(f"✓ Knowledge base: {len(self.chunks)} chunks from {len(self.documents)} documents")
        print(f"✓ Model: {MODEL}")

    def _initialize_rag(self):
        """Initialize RAG components: load documents and create vector store"""
        
        # Load documents from Knowledge_Base folder
        folders = glob.glob(f"{KNOWLEDGE_BASE_PATH}/*")
        
        def add_metadata(doc, doc_type):
            doc.metadata["doc_type"] = doc_type
            return doc
        
        text_loader_kwargs = {'encoding': 'utf-8'}
        
        self.documents = []
        for folder in folders:
            doc_type = os.path.basename(folder)
            loader = DirectoryLoader(
                folder, 
                glob="**/*.md", 
                loader_cls=TextLoader, 
                loader_kwargs=text_loader_kwargs
            )
            folder_docs = loader.load()
            self.documents.extend([add_metadata(doc, doc_type) for doc in folder_docs])
        
        # Split documents into chunks
        text_splitter = CharacterTextSplitter(
            chunk_size=CHUNK_SIZE, 
            chunk_overlap=CHUNK_OVERLAP,
            separator="\n\n",  # Split by paragraphs first
            length_function=len,
        )
        self.chunks = text_splitter.split_documents(self.documents)
        
        # Create embeddings and vector store
        embeddings = OpenAIEmbeddings()
        
        # Delete existing database if it exists
        if os.path.exists(DB_NAME):
            Chroma(persist_directory=DB_NAME, embedding_function=embeddings).delete_collection()
            print(f"✓ Cleared existing vector store")
        
        # Create new vectorstore
        vectorstore = Chroma.from_documents(
            documents=self.chunks, 
            embedding=embeddings, 
            persist_directory=DB_NAME
        )
        
        # Create retriever
        self.retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": TOP_K_RETRIEVAL}
        )
        
        print(f"✓ Vector store created with {vectorstore._collection.count()} documents")

    def evaluator_system_prompt(self):
        """Generate evaluator system prompt"""
        prompt = f"""You are an evaluator that decides whether a response to a question is acceptable. \
You are provided with a conversation between a User and an Agent. Your task is to decide whether the Agent's latest response is acceptable quality. \
The Agent is playing the role of {self.name} and is representing {self.name} on their website. \
The Agent has been instructed to be professional and engaging, as if talking to a potential client or future employer who came across the website. \
The Agent has been provided with context on {self.name} in the form of their summary and LinkedIn details. Here's the information:

## Summary:
{self.summary}

## LinkedIn Profile:
{self.linkedin}

With this context, please evaluate the latest response, replying with whether the response is acceptable and your feedback."""
        return prompt

    def evaluator_user_prompt(self, reply, message, history):
        """Generate evaluator user prompt"""
        # Format history for evaluation
        history_text = ""
        if history:
            for msg in history:
                role = msg.get("role", "")
                content = msg.get("content", "")
                if role == "user":
                    history_text += f"User: {content}\n"
                elif role == "assistant":
                    history_text += f"Assistant: {content}\n"
        
        user_prompt = f"Here's the conversation between the User and the Agent: \n\n{history_text}\n\n"
        user_prompt += f"Here's the latest message from the User: \n\n{message}\n\n"
        user_prompt += f"Here's the latest response from the Agent: \n\n{reply}\n\n"
        user_prompt += "Please evaluate the response, replying with whether it is acceptable and your feedback."
        return user_prompt

    def evaluate(self, reply, message, history) -> Evaluation:
        """Evaluate response quality using Gemini"""
        if not gemini:
            # If Gemini is not configured, always accept
            return Evaluation(is_acceptable=True, feedback="Evaluation skipped - Gemini not configured")
        
        messages = [
            {"role": "system", "content": self.evaluator_system_prompt()},
            {"role": "user", "content": self.evaluator_user_prompt(reply, message, history)}
        ]
        
        try:
            response = gemini.beta.chat.completions.parse(
                model=EVALUATOR_MODEL,
                messages=messages,
                response_format=Evaluation
            )
            return response.choices[0].message.parsed
        except Exception as e:
            print(f"⚠️ Evaluation failed: {e}")
            # If evaluation fails, accept the response
            return Evaluation(is_acceptable=True, feedback=f"Evaluation error: {str(e)}")

    def rerun(self, reply, message, history, feedback):
        """Regenerate response based on evaluation feedback"""
        # Retrieve context again
        docs = self.retriever.invoke(message)
        
        context_parts = []
        total_length = 0
        for doc in docs:
            doc_content = doc.page_content
            doc_type = doc.metadata.get('doc_type', 'Unknown')
            context_part = f"[{doc_type}]: {doc_content}"
            
            if total_length + len(context_part) > MAX_CONTEXT_LENGTH:
                remaining = MAX_CONTEXT_LENGTH - total_length
                if remaining > 100:
                    context_part = context_part[:remaining] + "..."
                    context_parts.append(context_part)
                break
            
            context_parts.append(context_part)
            total_length += len(context_part)
        
        context = "\n\n".join(context_parts)
        
        # Build updated system prompt with feedback
        updated_system_prompt = self.system_prompt() + "\n\n## Previous answer rejected\n"
        updated_system_prompt += "You just tried to reply, but the quality control rejected your reply.\n"
        updated_system_prompt += f"## Your attempted answer:\n{reply}\n\n"
        updated_system_prompt += f"## Reason for rejection:\n{feedback}\n\n"
        updated_system_prompt += "Please try again with a better response that addresses the feedback."
        
        # Build messages with context
        user_message_with_context = f"""Context: {context}

Question: {message}"""
        
        messages = [
            {"role": "system", "content": updated_system_prompt},
            {"role": "user", "content": user_message_with_context}
        ]
        
        # Generate new response (non-streaming for rerun)
        response = self.openai.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
            temperature=0.7
        )
        
        return response.choices[0].message.content

    def handle_tool_calls(self, tool_calls):
        """Execute tool calls and return results"""
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(f"🔧 Tool called: {tool_name}")
            
            # Get the function dynamically
            tool = globals().get(tool_name)
            result = tool(**arguments) if tool else {"error": "Tool not found"}
            
            results.append({
                "role": "tool",
                "content": json.dumps(result),
                "tool_call_id": tool_call.id
            })
        return results

    def system_prompt(self):
        """Generate system prompt with context"""
        prompt = f"""You are acting as {self.name}'s personal AI assistant. You are answering questions on {self.name}'s website, \
particularly questions related to {self.name}'s career, background, skills, and experience.

Your responsibilities:
1. Represent {self.name} faithfully and professionally for all interactions
2. Answer questions using ONLY the provided context from the knowledge base
3. Be concise and engaging, as if talking to a potential client or future employer
4. If you don't know the answer, use your record_unknown_question tool
5. If the user wants to connect, ask for their email and use the record_user_details tool

## Brief Summary:
{self.summary}

Note: Detailed information is provided in the retrieved context below.
"""
        return prompt

    def chat(self, message, history):
        """
        Main chat function with streaming that:
        1. Retrieves relevant context from the vector store (RAG)
        2. Streams responses from OpenAI with function calling
        3. Handles tool calls as needed
        """
        
        # Step 1: Retrieve relevant documents using RAG
        docs = self.retriever.invoke(message)
        
        # Optimize context: only include most relevant parts, limit total length
        context_parts = []
        total_length = 0
        for doc in docs:
            doc_content = doc.page_content
            doc_type = doc.metadata.get('doc_type', 'Unknown')
            context_part = f"[{doc_type}]: {doc_content}"
            
            if total_length + len(context_part) > MAX_CONTEXT_LENGTH:
                # Truncate to fit
                remaining = MAX_CONTEXT_LENGTH - total_length
                if remaining > 100:  # Only add if meaningful content fits
                    context_part = context_part[:remaining] + "..."
                    context_parts.append(context_part)
                break
            
            context_parts.append(context_part)
            total_length += len(context_part)
        
        context = "\n\n".join(context_parts)
        
        # Step 2: Build conversation history (limit to last 3 exchanges)
        history_text = ""
        if history:
            recent_history = history[-6:]  # Last 3 exchanges (6 messages)
            for msg in recent_history:
                role = msg.get("role", "")
                content = msg.get("content", "")
                if role == "user":
                    history_text += f"User: {content}\n"
                elif role == "assistant":
                    history_text += f"Assistant: {content}\n"
        
        # Step 3: Create concise user message with retrieved context
        user_message_with_context = f"""Context: {context}

Question: {message}"""
        
        if history_text:
            user_message_with_context = f"Recent conversation:\n{history_text}\n\n" + user_message_with_context
        
        # Step 4: Build messages array
        messages = [
            {"role": "system", "content": self.system_prompt()},
            {"role": "user", "content": user_message_with_context}
        ]
        
        # Step 5: Stream OpenAI response with function calling
        done = False
        max_iterations = 5
        iteration = 0
        final_response = ""
        
        while not done and iteration < max_iterations:
            iteration += 1
            
            # Use streaming for the final response
            stream = self.openai.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=tools,
                temperature=0.7,
                stream=True
            )
            
            # Collect streamed response
            collected_messages = []
            tool_calls_data = []
            finish_reason = None
            
            for chunk in stream:
                if chunk.choices:
                    delta = chunk.choices[0].delta
                    finish_reason = chunk.choices[0].finish_reason
                    
                    # Handle content
                    if delta.content:
                        collected_messages.append(delta.content)
                        final_response = "".join(collected_messages)
                        yield final_response  # Stream to UI
                    
                    # Handle tool calls
                    if delta.tool_calls:
                        for tool_call_chunk in delta.tool_calls:
                            # Initialize or update tool call data
                            if len(tool_calls_data) <= tool_call_chunk.index:
                                tool_calls_data.append({
                                    "id": "",
                                    "function": {"name": "", "arguments": ""}
                                })
                            
                            tc = tool_calls_data[tool_call_chunk.index]
                            if tool_call_chunk.id:
                                tc["id"] = tool_call_chunk.id
                            if tool_call_chunk.function:
                                if tool_call_chunk.function.name:
                                    tc["function"]["name"] = tool_call_chunk.function.name
                                if tool_call_chunk.function.arguments:
                                    tc["function"]["arguments"] += tool_call_chunk.function.arguments
            
            # Check if we need to handle tool calls
            if finish_reason == "tool_calls" and tool_calls_data:
                # Create tool call objects
                from types import SimpleNamespace
                tool_calls_list = []
                for tc_data in tool_calls_data:
                    tool_call = SimpleNamespace(
                        id=tc_data["id"],
                        function=SimpleNamespace(
                            name=tc_data["function"]["name"],
                            arguments=tc_data["function"]["arguments"]
                        )
                    )
                    tool_calls_list.append(tool_call)
                
                # Handle the tool calls
                results = self.handle_tool_calls(tool_calls_list)
                
                # Create message object for tool calls
                message_obj = {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in tool_calls_list
                    ]
                }
                
                messages.append(message_obj)
                messages.extend(results)
                # Reset for next iteration
                collected_messages = []
                final_response = ""
            else:
                done = True
        
        # Step 6: Evaluate response quality (if Gemini is configured)
        if final_response and gemini:
            print("🔍 Evaluating response quality...")
            evaluation = self.evaluate(final_response, message, history)
            
            if evaluation.is_acceptable:
                print("✅ Response passed evaluation")
            else:
                print("❌ Response failed evaluation - regenerating...")
                print(f"📝 Feedback: {evaluation.feedback}")
                final_response = self.rerun(final_response, message, history, evaluation.feedback)
                print("✅ New response generated")
        
        # Return final response (this ensures history is preserved)
        if final_response:
            return final_response
        else:
            return "I apologize, but I couldn't generate a response. Please try again."


if __name__ == "__main__":
    print("🚀 Launching Personal AI Assistant...")
    
    # Initialize Personal AI
    personal_ai = PersonalAI()
    
    # Optional: Force dark mode
    force_dark_mode = """
    function refresh() {
        const url = new URL(window.location);
        if (url.searchParams.get('__theme') !== 'dark') {
            url.searchParams.set('__theme', 'dark');
            window.location.href = url.href;
        }
    }
    """
    
    # Launch Gradio interface
    interface = gr.ChatInterface(
        personal_ai.chat,
        type="messages",
        title=f"Personal AI - {personal_ai.name}",
        description="Ask me anything about my background, experience, skills, and projects!",
        js=force_dark_mode
    )
    
    interface.launch(inbrowser=True, share=True)
