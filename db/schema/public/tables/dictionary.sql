create table dictionary (
    id serial,
    word_from_id integer not null,
    word_to_id integer not null,
    relation relation_mnemonic not null,
    authority smallint not null,
    user_id integer not null,
    constraint dictionary_authority_check CHECK ((authority > 0))
);

alter table only dictionary
    add constraint dictionary_word_from_id_fkey foreign key (word_from_id) references word(id);

alter table only dictionary
    add constraint dictionary_word_to_id_fkey foreign key (word_to_id) references word(id);

alter table only dictionary
    add constraint dictionary_pkey primary key (id);

create unique index dictionary_user_id_word_from_id_word_to_id_idx on dictionary using btree (user_id, word_from_id, word_to_id);

