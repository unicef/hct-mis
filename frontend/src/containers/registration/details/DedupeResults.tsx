import React, { useState } from 'react';
import styled from 'styled-components';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import {
  ImportedIndividualMinimalFragment,
  DeduplicationResultNode,
} from '../../../__generated__/graphql';
import { useHistory } from 'react-router-dom';
import { MiśTheme } from '../../../theme';
import { decodeIdString } from '../../../utils/utils';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import { useBusinessArea } from '../../../hooks/useBusinessArea';

const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;

const DialogDescription = styled.div`
  margin: 20px 0;
  font-size: 14px;
  color: rgba(0, 0, 0, 0.54);
`;
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
const Pointer = styled.span`
  cursor: pointer;
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
  const [open, setOpen] = useState(false);
  const history = useHistory();
  const businessArea = useBusinessArea();
  const useStyles = makeStyles((theme) => ({
    table: {
      minWidth: 100,
    },
  }));
  const classes = useStyles();

  function createData(hitId, score, proximityToScore) {
    return { hitId, score, proximityToScore };
  }

  const rows = results.map((result) => {
    return createData(result.hitId, result.score, result.proximityToScore);
  });
  const handleClickBatch = (id): void => {
    const path = `/${businessArea}/registration-data-import/individual/${id}`;
    history.push(path);
  };

  const handleClickGoldenRecord = (id): void => {
    const path = `/${businessArea}/population/individuals/${id}`;
    history.push(path);
  };
  return (
    <>
      <Error onClick={() => setOpen(true)}>
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
          <DialogTitle id='scroll-dialog-title'>Duplicates</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogDescription>
            <div>
              Duplicates of{' '}
              <Bold>
                {decodeIdString(individual.id)} {individual.fullName}
              </Bold>{' '}
              are listed below.
            </div>
          </DialogDescription>
          <Table className={classes.table}>
            <TableHead>
              <TableRow>
                <TableCell style={{ width: 100 }}>Individual ID</TableCell>
                <TableCell style={{ width: 100 }} align='right'>
                  Similarity Score
                </TableCell>
                <TableCell style={{ width: 100 }} align='right'>
                  Proximity to the Score
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((row) => (
                <TableRow key={row.hitId}>
                  <TableCell
                    onClick={() =>
                      isInBatch
                        ? handleClickBatch(row.hitId)
                        : handleClickGoldenRecord(row.hitId)
                    }
                    component='th'
                    scope='row'
                  >
                    <Pointer>{decodeIdString(row.hitId)}</Pointer>
                  </TableCell>
                  <TableCell align='right'>{row.score.toFixed(2)}</TableCell>
                  <TableCell align='right'>
                    {row.proximityToScore > 0 && '+'}{' '}
                    {row.proximityToScore.toFixed(2)}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setOpen(false)}>CLOSE</Button>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
}
