create table answer (
    id serial,
    job_id integer not null,
    date_time timestamp with time zone default now() not null,
    answer character varying,
    is_correct boolean not null
);

alter table only answer
    add constraint answer_job_id_fkey foreign key (job_id) references job(id);

alter table only answer
    add constraint answer_pkey primary key (id);

create unique index answer_job_id_idx on answer using btree (job_id) WHERE is_correct;

