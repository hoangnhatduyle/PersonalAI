alter table conversations
  add column response_id text,
  add column client_message_id text,
  add column feedback text check (feedback in ('up', 'down'));

create index idx_conversations_response_id on conversations (response_id);
create unique index idx_conversations_client_message_id on conversations (client_message_id);
