alter table patients add column lastvisit timestamp default current_timestamp;

alter table patients add column procedurecount int default 0;