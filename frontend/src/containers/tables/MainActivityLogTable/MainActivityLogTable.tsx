import { ReactElement, useState } from 'react';
import styled from 'styled-components';
import Collapse from '@mui/material/Collapse';
import { Box, IconButton, Paper } from '@mui/material';
import TablePagination from '@mui/material/TablePagination';
import { AllLogEntriesQuery, LogEntryNode } from '@generated/graphql';
import {
  ButtonPlaceHolder,
  Row,
} from '@components/core/ActivityLogTable/TableStyledComponents';
import { useArrayToDict } from '@hooks/useArrayToDict';
import { MainActivityLogTableRow } from './MainActivityLogTableRow';
import { headCells } from './MainActivityLogTableHeadCells';
import { KeyboardArrowLeft, KeyboardArrowRight } from '@mui/icons-material';

const Table = styled.div`
  display: flex;
  flex-direction: column;
`;
interface HeadingCellProps {
  weight?: number;
}

const HeadingCell = styled.div<HeadingCellProps>`
  display: flex;
  flex: ${({ weight }) => weight || 1};
  padding: 16px;
  font-size: 12px;
  text-align: left;
  font-weight: 500;
  line-height: 1.43rem;
  border-bottom: 1px solid rgba(224, 224, 224, 1);
  letter-spacing: 0.01071em;
  vertical-align: inherit;
`;

const PaperContainer = styled(Paper)`
  width: 100%;
  padding: ${({ theme }) => theme.spacing(5)} 0;
  margin-bottom: ${({ theme }) => theme.spacing(5)};
`;

interface MainActivityLogTableProps {
  logEntries: LogEntryNode[];
  totalCount: number;
  rowsPerPage: number;
  page: number;
  onChangePage: (event: unknown, newPage: number) => void;
  onChangeRowsPerPage: (event: React.ChangeEvent<HTMLInputElement>) => void;
  actionChoices: AllLogEntriesQuery['logEntryActionChoices'];
  loading: boolean;
}
export function MainActivityLogTable({
  logEntries,
  totalCount,
  rowsPerPage,
  page,
  onChangePage,
  onChangeRowsPerPage,
  actionChoices,
  loading = false,
}: MainActivityLogTableProps): ReactElement {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [expanded, setExpanded] = useState(true);
  const choicesDict = useArrayToDict(actionChoices, 'value', 'name');

  const TablePaginationActions = () => {
    const handleBackButtonClick = (event) => {
      onChangePage(event, page - 1);
    };

    const handleNextButtonClick = (event) => {
      onChangePage(event, page + 1);
    };

    return (
      <Box sx={{ flexShrink: 0, ml: 2.5 }}>
        <IconButton
          onClick={handleBackButtonClick}
          disabled={page === 0 || loading}
          aria-label="previous page"
        >
          <KeyboardArrowLeft />
        </IconButton>
        <IconButton
          onClick={handleNextButtonClick}
          disabled={page >= Math.ceil(totalCount / rowsPerPage) - 1 || loading}
          aria-label="next page"
        >
          <KeyboardArrowRight />
        </IconButton>
      </Box>
    );
  };

  return (
    <PaperContainer>
      <Collapse in={expanded}>
        <Table>
          <Row>
            {headCells.map((item) => (
              <HeadingCell key={item.id} style={{ flex: item.weight || 1 }}>
                {item.label}
              </HeadingCell>
            ))}
            <ButtonPlaceHolder />
          </Row>
          {logEntries.map((value) => (
            <MainActivityLogTableRow
              key={value.id}
              actionChoicesDict={choicesDict}
              logEntry={
                value as AllLogEntriesQuery['allLogEntries']['edges'][number]['node']
              }
            />
          ))}
        </Table>
        <TablePagination
          rowsPerPageOptions={[5, 10, 15, 20]}
          component="div"
          count={totalCount}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={onChangePage}
          onRowsPerPageChange={onChangeRowsPerPage}
          ActionsComponent={TablePaginationActions}
        />
      </Collapse>
    </PaperContainer>
  );
}
