import Step from '@mui/material/Step';
import StepLabel from '@mui/material/StepLabel';
import Stepper from '@mui/material/Stepper';
import CancelIcon from '@mui/icons-material/Cancel';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { PaymentPlanQuery } from '@generated/graphql';
import { StepIconProps } from '@mui/material';

const StyledCancelIcon = styled(CancelIcon)`
  color: #e90202;
`;

interface AcceptanceProcessStepperProps {
  acceptanceProcess: PaymentPlanQuery['paymentPlan']['approvalProcess']['edges'][0]['node'];
}

const StepIconWrapper: React.FC<StepIconProps> = (props) => {
  const { error } = props;
  return error ? <StyledCancelIcon /> : null;
};

export function AcceptanceProcessStepper({
  acceptanceProcess,
}: AcceptanceProcessStepperProps): React.ReactElement {
  const {
    rejectedOn,
    actions,
    approvalNumberRequired,
    authorizationNumberRequired,
    financeReleaseNumberRequired,
  } = acceptanceProcess;
  const { t } = useTranslation();
  const steps = [
    {
      name: `${t('Approval')} (${
        actions.approval.length
      }/${approvalNumberRequired})`,
      hasError: rejectedOn === 'IN_APPROVAL',
      isCompleted: actions.approval.length === approvalNumberRequired,
    },
    {
      name: `${t('Authorization')} (${
        actions.authorization.length
      }/${authorizationNumberRequired})`,
      hasError: rejectedOn === 'IN_AUTHORIZATION',
      isCompleted: actions.authorization.length === authorizationNumberRequired,
    },
    {
      name: `${t('Finance Release')} (${
        actions.financeRelease.length
      }/${financeReleaseNumberRequired})`,
      hasError: rejectedOn === 'IN_REVIEW',
      isCompleted:
        actions.financeRelease.length === financeReleaseNumberRequired,
    },
  ];
  const getActiveStep = (): number => {
    if (actions.authorization.length === authorizationNumberRequired) {
      return 2;
    }
    if (actions.approval.length === approvalNumberRequired) {
      return 1;
    }
    return 0;
  };

  return (
    <Stepper activeStep={getActiveStep()}>
      {steps.map((step) => (
        <Step completed={step.isCompleted} key={step.name}>
          <StepLabel
            error={step.hasError}
            StepIconComponent={step.hasError ? StepIconWrapper : undefined}
          >
            {step.name}
          </StepLabel>
        </Step>
      ))}
    </Stepper>
  );
}
