import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@material-ui/core';
import { Formik } from 'formik';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { DialogFooter } from '../../../../containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../../../containers/dialogs/DialogTitleWrapper';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { useGrievancesChoiceDataQuery } from '../../../../__generated__/graphql';
import { LoadingComponent } from '../../../core/LoadingComponent';
import { LookUpLinkedTicketsFilters } from '../LookUpLinkedTicketsTable/LookUpLinkedTicketsFilters';
import { LookUpLinkedTicketsTable } from '../LookUpLinkedTicketsTable/LookUpLinkedTicketsTable';

export const LookUpLinkedTicketsModal = ({
  onValueChange,
  initialValues,
  lookUpDialogOpen,
  setLookUpDialogOpen,
}): React.ReactElement => {
  const businessArea = useBusinessArea();
  const { t } = useTranslation();
  const filterInitial = {
    search: '',
    status: '',
    fsp: '',
    createdAtRange: '',
    admin: '',
  };
  const [filterApplied, setFilterApplied] = useState(filterInitial);
  const [filter, setFilter] = useState(filterInitial);
  const {
    data: choicesData,
    loading: choicesLoading,
  } = useGrievancesChoiceDataQuery();
  if (!choicesData) return null;
  if (choicesLoading) {
    return <LoadingComponent />;
  }
  return (
    <Formik
      initialValues={initialValues}
      onSubmit={(values) => {
        onValueChange('selectedLinkedTickets', values.selectedLinkedTickets);
        setLookUpDialogOpen(false);
      }}
    >
      {({ submitForm, setFieldValue }) => (
        <Dialog
          maxWidth='lg'
          fullWidth
          open={lookUpDialogOpen}
          onClose={() => setLookUpDialogOpen(false)}
          scroll='paper'
          aria-labelledby='form-dialog-title'
        >
          <DialogTitleWrapper>
            <DialogTitle id='scroll-dialog-title'>
              {t('Look up Linked Tickets')}
            </DialogTitle>
          </DialogTitleWrapper>
          <DialogContent>
            <LookUpLinkedTicketsFilters
              choicesData={choicesData}
              filter={filter}
              setFilterApplied={setFilterApplied}
              filterInitial={filterInitial}
              onFilterChange={setFilter}
            />
            <LookUpLinkedTicketsTable
              filter={filterApplied}
              businessArea={businessArea}
              setFieldValue={setFieldValue}
              initialValues={initialValues}
            />
          </DialogContent>
          <DialogFooter>
            <DialogActions>
              <Button onClick={() => setLookUpDialogOpen(false)}>
                {t('CANCEL')}
              </Button>
              <Button
                type='submit'
                color='primary'
                variant='contained'
                onClick={submitForm}
                data-cy='button-submit'
              >
                {t('SAVE')}
              </Button>
            </DialogActions>
          </DialogFooter>
        </Dialog>
      )}
    </Formik>
  );
};
