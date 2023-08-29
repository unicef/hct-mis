import OpenInNewRoundedIcon from '@material-ui/icons/OpenInNewRounded';
import React from 'react';
import { Box, Button } from '@material-ui/core';
import { ReactivateProgram } from '../../dialogs/programs/ReactivateProgram';
import {
  ProgramNode,
  useCashAssistUrlPrefixQuery,
} from '../../../__generated__/graphql';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { CopyProgram } from '../../dialogs/programs/CopyProgram';

export interface FinishedProgramDetailsPageHeaderPropTypes {
  program: ProgramNode;
  canActivate: boolean;
  canDuplicate: boolean;
  isPaymentPlanApplicable: boolean;
}

export const FinishedProgramDetailsPageHeaderButtons = ({
  program,
  canActivate,
  canDuplicate,
  isPaymentPlanApplicable,
}: FinishedProgramDetailsPageHeaderPropTypes): React.ReactElement => {
  const { data, loading } = useCashAssistUrlPrefixQuery({
    fetchPolicy: 'cache-first',
  });
  if (loading) return <LoadingComponent />;
  if (!data) return null;
  return (
    <Box display='flex' alignItems='center'>
      {canActivate && (
        <Box m={2}>
          <ReactivateProgram program={program} />
        </Box>
      )}
      {!isPaymentPlanApplicable && (
        <Box m={2}>
          <Button
            variant='contained'
            color='primary'
            component='a'
            disabled={!program.caHashId}
            href={`${data.cashAssistUrlPrefix}/&pagetype=entityrecord&etn=progres_program&id=/${program.caHashId}`}
            startIcon={<OpenInNewRoundedIcon />}
          >
            Open in CashAssist
          </Button>
        </Box>
      )}
      {canDuplicate && (
        <Box m={2}>
          <CopyProgram program={program} />
        </Box>
      )}
    </Box>
  );
};
