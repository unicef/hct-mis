import React from 'react';
import { BaseSection } from '@components/core/BaseSection';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Checkbox,
  Box,
} from '@mui/material';
import { useTranslation } from 'react-i18next';
import { ApprovePaymentPlansModal } from '@components/managerialConsole/ApprovePaymentPlansModal';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { useSnackbar } from '@hooks/useSnackBar';
import { BlackLink } from '@components/core/BlackLink';
import { useBaseUrl } from '@hooks/useBaseUrl';

interface ApprovalSectionProps {
  selectedApproved: any[];
  setSelectedApproved: (value: React.SetStateAction<any[]>) => void;
  handleSelect: (
    selected: any[],
    setSelected: (value: React.SetStateAction<any[]>) => void,
    id: any,
  ) => void;
  handleSelectAll: (
    ids: any[],
    selected: any[],
    setSelected: {
      (value: React.SetStateAction<any[]>): void;
      (arg0: any[]): void;
    },
  ) => void;
  inApprovalData: any;
  bulkAction: any;
}

export const ApprovalSection: React.FC<ApprovalSectionProps> = ({
  selectedApproved,
  setSelectedApproved,
  handleSelect,
  handleSelectAll,
  inApprovalData,
  bulkAction,
}) => {
  const { t } = useTranslation();
  const { businessArea } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const handleSelectAllApproved = () => {
    const ids = inApprovalData.results.map((plan) => plan.id);
    handleSelectAll(ids, selectedApproved, setSelectedApproved);
  };

  const allSelected = inApprovalData?.results?.every((plan) =>
    selectedApproved.includes(plan.id),
  );

  const selectedPlansUnicefIds = inApprovalData?.results
    .filter((plan) => selectedApproved.includes(plan.id))
    .map((plan) => plan.unicef_id);

  return (
    <BaseSection
      title={t('Payment Plans pending for Approval')}
      buttons={
        <ApprovePaymentPlansModal
          selectedPlansIds={selectedApproved}
          selectedPlansUnicefIds={selectedPlansUnicefIds}
          onApprove={async (_, comment) => {
            try {
              await bulkAction.mutateAsync({
                ids: selectedApproved,
                action: 'APPROVE',
                comment: comment,
              });
              showMessage(t('Payment Plan(s) Approved'));
              setSelectedApproved([]);
            } catch (e) {
              showMessage(e.message);
            }
          }}
        />
      }
    >
      <Table>
        <TableHead>
          <TableRow>
            <TableCell padding="checkbox" style={{ width: '10%' }}>
              <Box sx={{ flex: 1 }}>
                <Checkbox
                  checked={allSelected && selectedApproved.length > 0}
                  onClick={handleSelectAllApproved}
                />
              </Box>
            </TableCell>
            <TableCell align="left" style={{ width: '22.5%' }}>
              <Box sx={{ flex: 1 }}>{t('Payment Plan ID')}</Box>
            </TableCell>
            <TableCell align="left" style={{ width: '22.5%' }}>
              <Box sx={{ flex: 1 }}>{t('Programme Name')}</Box>
            </TableCell>
            <TableCell align="left" style={{ width: '22.5%' }}>
              <Box sx={{ flex: 1 }}>{t('Last Modified Date')}</Box>
            </TableCell>
            <TableCell align="left" style={{ width: '22.5%' }}>
              <Box sx={{ flex: 1 }}>{t('Sent for Approval by')}</Box>
            </TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {inApprovalData?.results?.map((plan: any) => (
            <TableRow key={plan.id}>
              <TableCell padding="checkbox">
                <Checkbox
                  checked={selectedApproved.includes(plan.id)}
                  onChange={() =>
                    handleSelect(selectedApproved, setSelectedApproved, plan.id)
                  }
                />
              </TableCell>
              <TableCell align="left">
                <BlackLink
                  to={`/${businessArea}/programs/${plan.program_id}/payment-module/${plan.isFollowUp ? 'followup-payment-plans' : 'payment-plans'}/${plan.id}`}
                  newTab={true}
                >
                  {plan.unicef_id}
                </BlackLink>
              </TableCell>
              <TableCell align="left">{plan.program}</TableCell>
              <TableCell align="left">
                <UniversalMoment>
                  {plan.last_approval_process_date}
                </UniversalMoment>
              </TableCell>
              <TableCell align="left">
                {plan.last_approval_process_by}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </BaseSection>
  );
};
