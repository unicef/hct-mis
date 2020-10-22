import React, { useState } from 'react';
import styled from 'styled-components';
import { Button, Tooltip } from '@material-ui/core';
import { FileCopy, EditRounded } from '@material-ui/icons';
import {
  TargetPopulationNode,
  useUnapproveTpMutation,
} from '../../../__generated__/graphql';
import { DuplicateTargetPopulation } from '../../dialogs/targetPopulation/DuplicateTargetPopulation';
import { FinalizeTargetPopulation } from '../../dialogs/targetPopulation/FinalizeTargetPopulation';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { useSnackbar } from '../../../hooks/useSnackBar';

const IconContainer = styled.span`
  button {
    color: #949494;
    min-width: 40px;
    svg {
      width: 20px;
      height: 20px;
    }
  }
`;

const ButtonContainer = styled.span`
  margin: 0 ${({ theme }) => theme.spacing(2)}px;
`;

export interface ApprovedTargetPopulationHeaderButtonsPropTypes {
  targetPopulation: TargetPopulationNode;
}

export function ApprovedTargetPopulationHeaderButtons({
  targetPopulation,
}: ApprovedTargetPopulationHeaderButtonsPropTypes): React.ReactElement {
  const [openDuplicate, setOpenDuplicate] = useState(false);
  const [openFinalize, setOpenFinalize] = useState(false);
  const { showMessage } = useSnackbar();
  const [mutate] = useUnapproveTpMutation();

  console.log('targetPopulation', targetPopulation);
  return (
    <div>
      <IconContainer>
        <Button onClick={() => setOpenDuplicate(true)}>
          <FileCopy />
        </Button>
      </IconContainer>
      <ButtonContainer>
        <Button
          color='primary'
          variant='outlined'
          onClick={() => {
            mutate({
              variables: { id: targetPopulation.id },
            }).then(() => {
              showMessage('Target Population Unlocked');
            });
          }}
          data-cy='button-target-population-unlocked'
        >
          Unlock
        </Button>
      </ButtonContainer>
      <ButtonContainer>
        <Tooltip
          title={
            targetPopulation.program.status !== 'ACTIVE'
              ? 'Assigned programme is not ACTIVE'
              : 'Send to cash assist'
          }
        >
          <span>
            <Button
              variant='contained'
              color='primary'
              disabled={targetPopulation.program.status !== 'ACTIVE'}
              onClick={() => setOpenFinalize(true)}
              data-cy='button-target-population-send-to-cash-assist'
            >
              Send to cash assist
            </Button>
          </span>
        </Tooltip>
      </ButtonContainer>
      <DuplicateTargetPopulation
        open={openDuplicate}
        setOpen={setOpenDuplicate}
        targetPopulationId={targetPopulation.id}
      />
      <FinalizeTargetPopulation
        open={openFinalize}
        setOpen={setOpenFinalize}
        targetPopulationId={targetPopulation.id}
        totalHouseholds={targetPopulation.finalListTotalHouseholds}
      />
    </div>
  );
}
