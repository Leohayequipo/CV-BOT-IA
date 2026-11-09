-- One row per chunk. Applied on every ingestion, so each statement is safe to repeat.
create extension if not exists vector;

create table if not exists chunks (
    id text primary key,
    source_id text not null,
    title text not null,
    section text not null,
    content text not null,
    content_hash text not null,
    embedding vector(1536) not null,
    -- Keyword search (step 5.2): exact names like "FilamentPHP" beat embeddings
    fts tsvector generated always as (
        to_tsvector('english', title || ' ' || section || ' ' || content)
    ) stored,
    updated_at timestamptz not null default now()
);

create index if not exists chunks_fts_idx on chunks using gin (fts);
create index if not exists chunks_embedding_idx on chunks using hnsw (embedding vector_cosine_ops);

-- Supabase exposes public tables through its own API; with no policy, only the backend's
-- direct connection can read or write this one.
alter table chunks enable row level security;
