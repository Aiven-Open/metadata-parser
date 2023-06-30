create table metadata_parser_nodes(
    id text,
    json_content jsonb,
    primary key (id));

create table metadata_parser_edges(
    source_id text,
    destination_id text,
    json_content jsonb,
    primary key (source_id, destination_id),
    constraint fk_source_id foreign key (source_id) references metadata_parser_nodes(id),
    constraint fk_destination_id foreign key (destination_id) references metadata_parser_nodes(id)
    );

CREATE INDEX metadata_parser_nodes_idx ON metadata_parser_nodes USING GIN (json_content);

CREATE INDEX metadata_parser_edges_idx ON metadata_parser_edges USING GIN (json_content);

COMMIT;
