import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@mui/material';
import { makeStyles } from '@mui/material/styles';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { BlackLink } from '../../core/BlackLink';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { MiśTheme } from '../../../theme';
import { decodeIdString } from '../../../utils/utils';
import {
  DeduplicationResultNode,
  ImportedIndividualMinimalFragment,
} from '../../../__generated__/graphql';
import { DialogFooter } from '../../../containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../../containers/dialogs/DialogTitleWrapper';
import { DialogDescription } from '../../../containers/dialogs/DialogDescription';

const Error = styled.span`
  color: ${({ theme }: { theme: MiśTheme }) => theme.hctPalette.red};
  font-weight: bold;
  text-decoration: underline;
  cursor: pointer;
`;
const Bold = styled.span`
  font-weight: bold;
  font-size: 16px;
`;

interface DedupeResultsProps {
  individual: ImportedIndividualMinimalFragment;
  status: string;
  results: Array<DeduplicationResultNode>;
  isInBatch?: boolean;
}

export function DedupeResults({
  individual,
  status,
  results,
  isInBatch = false,
}: DedupeResultsProps): React.ReactElement {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const businessArea = useBusinessArea();
  const useStyles = makeStyles(() => ({
    table: {
      minWidth: 100,
    },
  }));
  const classes = useStyles();
  function createData(
    hitId,
    fullName,
    age,
    location,
    score,
    proximityToScore,
  ): {
    hitId: number;
    fullName: string;
    age: number;
    location: string;
    score: number;
    proximityToScore: number;
  } {
    return { hitId, fullName, age, location, score, proximityToScore };
  }
  const rows = results.map((result) => {
    return createData(
      result.hitId,
      result.fullName,
      result.age,
      result.location,
      result.score,
      result.proximityToScore,
    );
  });
  const handleClickBatch = (id): string => {
    const path = `/${businessArea}/registration-data-import/individual/${id}`;
    return path;
  };

  const handleClickGoldenRecord = (id): string => {
    const path = `/${businessArea}/population/individuals/${id}`;
    return path;
  };
  return (
    <>
      <Error
        onClick={(e) => {
          e.stopPropagation();
          setOpen(true);
        }}
      >
        {status} ({results.length})
      </Error>
      <Dialog
        maxWidth='md'
        fullWidth
        open={open}
        onClose={() => setOpen(false)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
      >
        <DialogTitleWrapper>
          <DialogTitle id='scroll-dialog-title'>{t('Duplicates')}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogDescription>
            <div>
              {t('Duplicates of')}{' '}
              <Bold>
                {individual.fullName} ({decodeIdString(individual.id)})
              </Bold>{' '}
              {isInBatch ? t('within batch ') : t('against population ')}
              {t('are listed below.')}
            </div>
          </DialogDescription>
          <Table className={classes.table}>
            <TableHead>
              <TableRow>
                <TableCell style={{ width: 100 }}>
                  {t('Individual ID')}
                </TableCell>
                <TableCell style={{ width: 100 }}>{t('Full Name')}</TableCell>
                <TableCell style={{ width: 100 }}>{t('Age')}</TableCell>
                <TableCell style={{ width: 100 }}>
                  {t('Administrative Level 2')}
                </TableCell>
                <TableCell style={{ width: 100 }} align='left'>
                  {t('Similarity Score')}
                </TableCell>
                <TableCell style={{ width: 100 }} align='left'>
                  {t('Proximity to the Score')}
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((row) => (
                <TableRow key={row.hitId}>
                  <TableCell>
                    <BlackLink
                      to={
                        isInBatch
                          ? handleClickBatch(row.hitId)
                          : handleClickGoldenRecord(row.hitId)
                      }
                    >
                      {decodeIdString(row.hitId)}
                    </BlackLink>
                  </TableCell>
                  <TableCell align='left'>{row.fullName}</TableCell>
                  <TableCell align='left'>
                    {row.age || t('Not provided')}
                  </TableCell>
                  <TableCell align='left'>{row.location}</TableCell>
                  <TableCell align='left'>{row.score}</TableCell>
                  <TableCell align='left'>
                    {row.proximityToScore > 0 && '+'} {row.proximityToScore}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button
              onClick={(e) => {
                setOpen(false);
                e.stopPropagation();
              }}
            >
              {t('CLOSE')}
            </Button>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
}
