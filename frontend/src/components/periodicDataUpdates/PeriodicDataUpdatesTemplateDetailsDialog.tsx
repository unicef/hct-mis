import React from 'react';
import { useTranslation } from 'react-i18next';
import { Template } from './PeriodicDataUpdatesTemplatesList';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  DialogActions,
  Button,
} from '@mui/material';
import { LabelizedField } from '@components/core/LabelizedField';
import { fetchPeriodicDataUpdateTemplateDetails } from '@api/periodicDataUpdate';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useQuery } from '@tanstack/react-query';
import { LoadingComponent } from '@components/core/LoadingComponent';

interface PeriodicDataUpdatesTemplateDetailsDialogProps {
  open: boolean;
  onClose: () => void;
  template: Template;
}

interface RoundDetails {
  round: number;
  round_name: string;
  number_of_records: number;
}
interface RoundDataItem {
  [key: string]: RoundDetails;
}

export const PeriodicDataUpdatesTemplateDetailsDialog: React.FC<
  PeriodicDataUpdatesTemplateDetailsDialogProps
> = ({ open, onClose, template }) => {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();
  const { data: templateDetailsData, isLoading } = useQuery({
    queryKey: [
      'periodicDataUpdateTemplateDetails',
      businessArea,
      programId,
      template.id,
    ],
    queryFn: () =>
      fetchPeriodicDataUpdateTemplateDetails(
        businessArea,
        programId,
        template.id,
      ),
  });

  if (isLoading) return <LoadingComponent />;

  return (
    <Dialog open={open} onClose={onClose} scroll="paper">
      <DialogTitle>{t('Periodic Data Updates')}</DialogTitle>
      <DialogContent>
        <LabelizedField label={t('Template Id')}>{template.id}</LabelizedField>
        {templateDetailsData && (
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>{t('Field')}</TableCell>
                <TableCell>{t('Round Number')}</TableCell>
                <TableCell>{t('Round Name')}</TableCell>
                <TableCell>{t('Number of individuals')}</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {templateDetailsData.rounds_data?.map(
                (roundData: RoundDataItem, index) => {
                  const [field, details] = Object.entries(roundData)[0];
                  return (
                    <TableRow key={index}>
                      <TableCell>{field}</TableCell>
                      <TableCell>{details.round}</TableCell>
                      <TableCell>{details.round_name}</TableCell>
                      <TableCell>{details.number_of_records}</TableCell>
                    </TableRow>
                  );
                },
              )}
            </TableBody>
          </Table>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>{t('Close')}</Button>
      </DialogActions>
    </Dialog>
  );
};
