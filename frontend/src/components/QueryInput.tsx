import React from 'react';
import { Input, Button, HStack } from '@chakra-ui/react';

type QueryInputProps = {
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onAdd: () => void;
};

const QueryInput: React.FC<QueryInputProps> = ({ value, onChange, onAdd }) => (
  <HStack>
    <Input
      placeholder="Enter search query"
      value={value}
      onChange={onChange}
      onKeyDown={e => e.key === 'Enter' && onAdd()}
    />
    <Button onClick={onAdd} colorScheme="teal">Add</Button>
  </HStack>
);

export default QueryInput; 