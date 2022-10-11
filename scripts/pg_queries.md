# Check the Nodes

```
select id, json_content from metadata_parser_nodes where id='pg~demo-pg~database~defaultdb';
```

```
select json_content from metadata_parser_nodes where id='service_type~pg~service_name~demo-pg~backup~2022-10-11_07-01_0.00000000.pghoard';
```

```
select json_content from metadata_parser_nodes where id='opensearch~demo-opensearch~index~my_pg_source.public.pasta';
```

# Check the Edges

```
select * from metadata_parser_edges;
```

# Explain filtering not using index

```
explain select id, json_content from metadata_parser_nodes where 
json_content ->> 'type' = 'user';
```

# Explain filtering using index
```
explain select id, json_content from metadata_parser_nodes where 
json_content @> '{"type": "user"}';
```

# Recursive query to get the users who can interact with the `pasta` TABLE

```
with recursive paths (id, last_label, last_type, last_service_type, list_of_edges, nr_items) as (
	select 
		id, 
		json_content ->> 'label',
		json_content ->> 'type',
		json_content ->> 'service_type',
		ARRAY[((n.json_content ->> 'type') || ':' || (n.json_content ->> 'label'))],
		1
	from metadata_parser_nodes n 
	where json_content ->> 'label' = 'pasta' 
	UNION ALL
	select 
		n.id,
		n.json_content ->> 'label',
		n.json_content ->> 'type',
		n.json_content ->> 'service_type',
		list_of_edges || ((n.json_content ->> 'type') || ':' || (n.json_content ->> 'label')),
		nr_items + 1
	from paths p 
	join metadata_parser_edges e on p.id = e.source_id
	join metadata_parser_nodes n on e.destination_id = n.id
	where
		1=1
		and n.json_content ->> 'type' <> 'service'
	) CYCLE id SET is_cycle USING items_ids
select last_label, last_type, last_service_type, list_of_edges from paths where is_cycle = False and last_type = 'user' order by nr_items;
```