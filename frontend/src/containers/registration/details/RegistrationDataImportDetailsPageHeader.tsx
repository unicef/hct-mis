import { Button } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import { BreadCrumbsItem } from '../../../components/BreadCrumbs';
import { PageHeader } from '../../../components/PageHeader';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import {
  RegistrationDataImportStatus,
  RegistrationDetailedFragment,
  useRefuseRdiMutation,
} from '../../../__generated__/graphql';
import { MergeRegistrationDataImportDialog } from './MergeRegistrationDataImportDialog';
import { RerunDedupe } from './RerunDedupe';

export interface RegistrationDataImportDetailsPageHeaderPropTypes {
  registration: RegistrationDetailedFragment;
  canMerge: boolean;
  canRerunDedupe: boolean;
  canViewList: boolean;
  canRefuse: boolean;
}

const MergeButtonContainer = styled.span`
  margin-left: ${({ theme }) => theme.spacing(4)}px;
`;

export function RegistrationDataImportDetailsPageHeader({
  registration,
  canMerge,
  canRerunDedupe,
  canViewList,
  canRefuse,
}: RegistrationDataImportDetailsPageHeaderPropTypes): React.ReactElement {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const [mutate] = useRefuseRdiMutation();
  let buttons = null;
  // eslint-disable-next-line default-case
  switch (registration?.status) {
    case RegistrationDataImportStatus.InReview:
      buttons = (
        <div>
          {canMerge && canRefuse && (
            <Button
              onClick={() =>
                mutate({
                  variables: { id: registration.id },
                })
              }
              variant='contained'
              color='primary'
            >
              {t('Refuse Import')}
            </Button>
          )}
          {canMerge && (
            <MergeButtonContainer>
              <MergeRegistrationDataImportDialog registration={registration} />
            </MergeButtonContainer>
          )}
        </div>
      );
      break;
    case RegistrationDataImportStatus.DeduplicationFailed:
      buttons = (
        <div>
          {canRerunDedupe && (
            <MergeButtonContainer>
              <RerunDedupe registration={registration} />
            </MergeButtonContainer>
          )}
        </div>
      );
      break;
    case RegistrationDataImportStatus.Merged:
      buttons = (
        <div>
          (
            <MergeButtonContainer>
              <Button
                variant='contained'
                color='primary'
                component={Link}
                to={`/${businessArea}/grievance-and-feedback/rdi/${registration.id}`}
              >
                {t('View Tickets')}
              </Button>
            </MergeButtonContainer>
          )
        </div>
      );
      break;
  }

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Registration Data import'),
      to: `/${businessArea}/registration-data-import/`,
    },
  ];
  return (
    <PageHeader
      title={registration.name}
      breadCrumbs={canViewList ? breadCrumbsItems : null}
    >
      {buttons}
    </PageHeader>
  );
}
