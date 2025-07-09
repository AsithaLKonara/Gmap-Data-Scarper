import React from 'react';
import { List, ListItem, IconButton } from '@chakra-ui/react';
import { CloseIcon } from '@chakra-ui/icons';

type QueryListProps = {
  queries: string[];
  onRemove: (q: string) => void;
};

const QueryList: React.FC<QueryListProps> = ({ queries, onRemove }) => (
  <List spacing={2}>
    {queries.map(q => (
      <ListItem key={q} display="flex" alignItems="center" justifyContent="space-between" bg="white" p={2} borderRadius="md" boxShadow="sm">
        <span>{q}</span>
        <IconButton aria-label="Remove" icon={<CloseIcon />} size="xs" onClick={() => onRemove(q)} />
      </ListItem>
    ))}
  </List>
);

export default QueryList; 