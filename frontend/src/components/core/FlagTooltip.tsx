import React from 'react';
import FlagIcon from '@material-ui/icons/Flag';
import { Tooltip } from '@material-ui/core';
import styled from 'styled-components';

const StyledFlag = styled(FlagIcon)`
  color: ${({ theme, confirmed }) =>
    confirmed ? 'deeppink' : theme.hctPalette.orange};
`;
interface FlagTooltipProps {
  confirmed?: boolean;
  message?: string;
}
export const FlagTooltip = ({
  confirmed,
  message = '',
}: FlagTooltipProps): React.ReactElement => {
  return (
    <Tooltip title={message}>
      <StyledFlag confirmed={confirmed} />
    </Tooltip>
  );
};
