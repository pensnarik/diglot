create table job (
    id serial,
    user_id bigint not null,
    date_time timestamp with time zone default now() not null,
    word_id integer,
    to_language language_mnemonic,
    status job_status_mnemonic default 'answering' not null
);

alter table only job
    add constraint job_pkey primary key (id);

create unique index job_user_id_idx on job using btree (user_id) WHERE (status = 'answering'::job_status_mnemonic);

