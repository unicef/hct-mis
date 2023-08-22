import React from 'react';
import { useTranslation } from 'react-i18next';
import { useParams, useLocation } from 'react-router-dom';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { BreadCrumbsItem } from '../../core/BreadCrumbs';
import { PageHeader } from '../../core/PageHeader';

interface SetUpPaymentInstructionsHeaderProps {
  baseUrl: string;
  permissions: string[];
}

export const SetUpPaymentInstructionsHeader = ({
  baseUrl,
  permissions,
}: SetUpPaymentInstructionsHeaderProps): React.ReactElement => {
  const location = useLocation();
  const { t } = useTranslation();
  const { id } = useParams();
  const isFollowUp = location.pathname.indexOf('followup') !== -1;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Payment Module'),
      to: `/${baseUrl}/payment-module/${
        isFollowUp ? 'followup-payment-plans' : 'payment-plans'
      }/${id}`,
    },
  ];

  return (
    <PageHeader
      title={t('Set up Payment Instruction')}
      breadCrumbs={
        hasPermissions(PERMISSIONS.PM_LOCK_AND_UNLOCK_FSP, permissions)
          ? breadCrumbsItems
          : null
      }
    />
  );
};
