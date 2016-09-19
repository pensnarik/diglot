create or replace
function get_correct_answer(ajob_id integer) returns character varying[] as $$
    select array_agg(wd.word)
      from public.job j
      join public.word w on w.id = j.word_id
      join public.dictionary d on d.word_from_id = w.id
      join public.word wd on wd.id = d.word_to_id
     where j.id = ajob_id and wd.language = j.to_language and
           d.relation = 'translate';
$$ language sql security definer;

