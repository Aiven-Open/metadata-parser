create table dogs (dogs_id serial, dogs_name varchar(100), age int, primary key(dogs_id));
insert into dogs(dogs_name, age) values ('Fuffi',8),('Roger',7),('Sandro',9);

create table dog_friend(dog_id int, friend_name varchar(100), constraint dog_exitst_fk foreign key(dog_id) references dogs(dogs_id));
insert into dog_friend values(1, 'Francesco'), (2, 'Ewelina'), (3, 'Lorna');


create view vw_dog_view AS
select dogs.dogs_id, dogs_name, age, friend_name
from dogs join dog_friend on dogs.dogs_id = dog_friend.dog_id;
