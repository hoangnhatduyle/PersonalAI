create table conversations (
  id bigint generated always as identity primary key,
  created_at timestamptz not null default now(),
  user_message text not null,
  assistant_response text not null,
  topic text
);

create index idx_conversations_created_at on conversations (created_at desc);
