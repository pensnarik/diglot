create table lang (
    id language_mnemonic not null,
    name character varying not null
);

alter table only lang
    add constraint lang_pkey primary key (id);

alter table only lang
    add constraint lang_name_key unique (name);

