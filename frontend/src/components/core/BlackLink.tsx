import React from 'react';
import styled from 'styled-components';
import { Link } from 'react-router-dom';

export const StyledLink = styled(Link)`
  color: #000;
  max-width: ${(props) => (props.fullWidth ? '100%' : '200px')}
  white-space: wrap;
  display: inline-block;
`;

export function BlackLink(props): React.ReactElement {
  return <StyledLink {...props} onClick={(e) => e.stopPropagation()} />;
}
