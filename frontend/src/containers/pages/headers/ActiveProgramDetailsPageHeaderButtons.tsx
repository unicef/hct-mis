import { Button } from '@material-ui/core';
import styled from 'styled-components';
import OpenInNewRoundedIcon from '@material-ui/icons/OpenInNewRounded';
import React from 'react';
import { ProgramNode } from '../../../__generated__/graphql';
import { FinishProgram } from '../../dialogs/programs/FinishProgram';
import { EditProgram } from '../../dialogs/programs/EditProgram';

const ButtonContainer = styled.span`
  margin: 0 ${({ theme }) => theme.spacing(2)}px;
`;

export interface ActiveProgramDetailsPageHeaderPropTypes {
  program: ProgramNode;
}
export function ActiveProgramDetailsPageHeaderButtons({
  program,
}: ActiveProgramDetailsPageHeaderPropTypes): React.ReactElement {
  return (
    <div>
      <ButtonContainer>
        <FinishProgram program={program} />
      </ButtonContainer>
      <ButtonContainer>
        <EditProgram program={program} />
      </ButtonContainer>
      <ButtonContainer>
        <Button
          variant='contained'
          color='primary'
          startIcon={<OpenInNewRoundedIcon />}
        >
          Open in CashAssist
        </Button>
      </ButtonContainer>
    </div>
  );
}
