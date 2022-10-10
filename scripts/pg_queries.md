# Check the Nodes

```
select id, json_content from metadata_parser_nodes;
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
with recursive paths (id, last_type, last_service_type, list_of_edges, nr_items) as (
	select 
		id, 
		json_content ->> 'type',
		json_content ->> 'service_type',
		ARRAY[jsonb_build_object('label', json_content ->> 'label', 'type', json_content ->> 'type')],
		1
	from metadata_parser_nodes n 
	where json_content ->> 'label' = 'pasta' 
	UNION ALL
	select 
		n.id,
		n.json_content ->> 'type',
		n.json_content ->> 'service_type',
		list_of_edges || jsonb_build_object('label', n.json_content ->> 'label', 'type', n.json_content ->> 'type'),
		nr_items + 1
	from paths p 
	join metadata_parser_edges e on p.id = e.source_id
	join metadata_parser_nodes n on e.destination_id = n.id
	where
		1=1
		and n.json_content ->> 'type' <> 'service'
	) CYCLE id SET is_cycle USING items_ids
select * from paths where is_cycle = False and last_type = 'user' order by nr_items;
```