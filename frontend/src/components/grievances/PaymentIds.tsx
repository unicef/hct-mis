import { Box, Typography } from '@mui/material';
import React from 'react';
import { useTranslation } from 'react-i18next';
import {
  PaymentRecordNode,
  PaymentVerificationNode,
} from '../../__generated__/graphql';
import { useBaseUrl } from '../../hooks/useBaseUrl';
import { ContentLink } from '../core/ContentLink';
import { Title } from '../core/Title';
import { ApproveBox } from './GrievancesApproveSection/ApproveSectionStyles';

type VerificationId = {
  id: PaymentVerificationNode['id'];
  caId: PaymentRecordNode['caId'];
};

interface PaymentIdsProps {
  verifications: VerificationId[];
}

export function PaymentIds({
  verifications,
}: PaymentIdsProps): React.ReactElement {
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();

  const mappedIds = verifications.map(
    (verification): React.ReactElement => (
      <Box mb={1}>
        <ContentLink
          href={`/${baseUrl}/verification-records/${verification.id}`}
        >
          {verification.caId}
        </ContentLink>
      </Box>
    ),
  );
  return (
    <ApproveBox>
      <Title>
        <Typography variant="h6">{t('Payment Ids')}</Typography>
      </Title>
      <Box display="flex" flexDirection="column">
        {mappedIds}
      </Box>
    </ApproveBox>
  );
}
