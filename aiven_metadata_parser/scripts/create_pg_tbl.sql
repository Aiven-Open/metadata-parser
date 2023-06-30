create table pasta (pasta_id serial, pasta_name varchar(100), cooking_minutes int, primary key(pasta_id));
insert into pasta(pasta_name, cooking_minutes) values ('pennette',8),('fusilli',7),('spaghetti',9);

create table pasta_eater(pasta_id int, eater_name varchar(100), constraint pasta_exitst_fk foreign key(pasta_id) references pasta(pasta_id));
insert into pasta_eater values(1, 'Francesco'), (2, 'Ewelina'), (3, 'Lorna');


create view vw_pasta_view AS
select pasta.pasta_id, pasta_name, cooking_minutes, eater_name
from pasta join pasta_eater on pasta.pasta_id = pasta_eater.pasta_id;
