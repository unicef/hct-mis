import {Button} from '@material-ui/core';
import React from 'react';
import {useTranslation} from 'react-i18next';
import {Link} from 'react-router-dom';
import styled from 'styled-components';
import {useBusinessArea} from '../../../hooks/useBusinessArea';
import {
  RegistrationDataImportStatus,
  RegistrationDetailedFragment,
  useRefuseRdiMutation,
  useEraseRdiMutation
} from '../../../__generated__/graphql';
import {BreadCrumbsItem} from '../../core/BreadCrumbs';
import {LoadingButton} from '../../core/LoadingButton';
import {PageHeader} from '../../core/PageHeader';
import {MergeRegistrationDataImportDialog} from './MergeRegistrationDataImportDialog';
import {RerunDedupe} from './RerunDedupe';
import {useConfirmation} from "../../core/ConfirmationDialog";

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
  const confirm = useConfirmation();
  const [mutate, { loading }] = useRefuseRdiMutation();
  const [eraseRdiMutate, { loading: eraseLoading }] = useEraseRdiMutation();

  let buttons = null;

  const eraseButton = (
      <LoadingButton
        loading={eraseLoading}
        onClick={() =>
         confirm({
            title: t('Warning'),
            content: t('Are you sure you want to erase RDI? Erasing RDI causes deletion of all related datahub RDI data'),
          }).then(async () => {
            await eraseRdiMutate({
              variables: { id: registration.id },
            })
          })
        }
        variant='contained'
        color='primary'
      >
        {t('Erase import')}
      </LoadingButton>
  )
  // eslint-disable-next-line default-case
  switch (registration?.status) {
    case RegistrationDataImportStatus.ImportError:
    case RegistrationDataImportStatus.MergeError:
      buttons = (
        <div>
          {canRefuse && eraseButton}
        </div>
      );
      break;
    case RegistrationDataImportStatus.InReview:
      buttons = (
        <div>
          {canMerge && canRefuse && (
            <LoadingButton
              loading={loading}
              onClick={() =>
                mutate({
                  variables: { id: registration.id },
                })
              }
              variant='contained'
              color='primary'
            >
              {t('Refuse Import')}
            </LoadingButton>
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
          {canRefuse && eraseButton}
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
      isErased={registration.erased}
    >
      {registration.erased ? null : buttons}
    </PageHeader>
  );
}
