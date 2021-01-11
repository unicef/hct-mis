import OpenInNewRoundedIcon from '@material-ui/icons/OpenInNewRounded';
import React from 'react';
import styled from 'styled-components';
import { Button } from '@material-ui/core';
import { ReactivateProgram } from '../../dialogs/programs/ReactivateProgram';
import { ProgramNode } from '../../../__generated__/graphql';

const ButtonContainer = styled.span`
  margin: 0 ${({ theme }) => theme.spacing(2)}px;
`;
export interface FinishedProgramDetailsPageHeaderPropTypes {
  program: ProgramNode;
  canActivate: boolean;
}

export function FinishedProgramDetailsPageHeaderButtons({
  program,
  canActivate,
}: FinishedProgramDetailsPageHeaderPropTypes): React.ReactElement {
  return (
    <div>
      {canActivate && (
        <ButtonContainer>
          <ReactivateProgram program={program} />
        </ButtonContainer>
      )}
      <ButtonContainer>
        <Button
          variant='contained'
          color='primary'
          component='a'
          href={`/cashassist/${program.caId}`}
          startIcon={<OpenInNewRoundedIcon />}
        >
          Open in CashAssist
        </Button>
      </ButtonContainer>
    </div>
  );
}
