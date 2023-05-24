import { Box } from '@material-ui/core';
import Paper from '@material-ui/core/Paper';
import { createStyles, makeStyles, Theme } from '@material-ui/core/styles';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableContainer from '@material-ui/core/TableContainer';
import TablePagination from '@material-ui/core/TablePagination';
import TableRow from '@material-ui/core/TableRow';
import FindInPageIcon from '@material-ui/icons/FindInPage';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { LoadingComponent } from '../LoadingComponent';
import { EnhancedTableHead, HeadCell } from './EnhancedTableHead';
import { EnhancedTableToolbar } from './EnhancedTableToolbar';

export type Order = 'asc' | 'desc';

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    root: {
      width: '100%',
    },
    paper: {
      width: '100%',
      marginBottom: theme.spacing(2),
    },
    table: {
      minWidth: 750,
    },
    empty: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      flexDirection: 'column',
      color: 'rgba(0, 0, 0, 0.38)',
      fontSize: '24px',
      lineHeight: '28px',
      textAlign: 'center',
      padding: '70px',
    },
    smallerText: {
      fontSize: '16px',
    },
    icon: {
      fontSize: '50px',
    },
  }),
);

interface TableComponentProps<T> {
  data: T[];
  renderRow: (row: T) => React.ReactElement;
  headCells: HeadCell<T>[];
  rowsPerPageOptions: number[];
  rowsPerPage: number;
  page: number;
  itemsCount: number;
  handleChangePage: (event: unknown, newPage: number) => void;
  handleChangeRowsPerPage: (event: React.ChangeEvent<HTMLInputElement>) => void;
  handleRequestSort: (
    event: React.MouseEvent<unknown>,
    property: string,
  ) => void;
  orderBy: string;
  order: Order;
  title?: string;
  loading?: boolean;
  allowSort?: boolean;
  isOnPaper?: boolean;
  actions?: Array<React.ReactElement>;
  onSelectAllClick?: (event, rows) => void;
  numSelected?: number;
}

export function TableComponent<T>({
  title = '',
  renderRow,
  data,
  headCells,
  rowsPerPageOptions,
  rowsPerPage,
  page,
  itemsCount,
  handleChangePage,
  handleChangeRowsPerPage,
  handleRequestSort,
  order,
  orderBy,
  loading = false,
  allowSort = true,
  isOnPaper = true,
  actions = [],
  onSelectAllClick,
  numSelected = 0,
}: TableComponentProps<T>): React.ReactElement {
  const { t } = useTranslation();
  const classes = useStyles({});

  const emptyRows = itemsCount
    ? rowsPerPage - Math.min(rowsPerPage, itemsCount - page * rowsPerPage)
    : rowsPerPage;
  let body;
  if (loading) {
    body = (
      <TableRow style={{ height: 54 * rowsPerPage, minHeight: 54 }}>
        <TableCell colSpan={headCells.length}>
          <LoadingComponent />
        </TableCell>
      </TableRow>
    );
  } else if (!data.length) {
    body = (
      <TableRow style={{ height: 54 * emptyRows, minHeight: 54 }}>
        <TableCell colSpan={headCells.length}>
          <div className={classes.empty}>
            <FindInPageIcon className={classes.icon} fontSize='inherit' />
            <Box mt={2}>No results</Box>
            <Box className={classes.smallerText} mt={2}>
              {t(
                'Try adjusting your search or your filters to find what you are looking for.',
              )}
            </Box>
          </div>
        </TableCell>
      </TableRow>
    );
  } else {
    body = (
      <>
        {data.map((row) => {
          return renderRow(row);
        })}
        {emptyRows > 0 && (
          <TableRow style={{ height: 54 * emptyRows }}>
            <TableCell colSpan={headCells.length} />
          </TableRow>
        )}
      </>
    );
  }
  const table = (
    <>
      <TableContainer>
        <Box display='flex' justifyContent='space-between'>
          {title ? <EnhancedTableToolbar title={title} /> : null}
          <Box p={5} display='flex'>
            {actions || null}
          </Box>
        </Box>

        <Table
          className={classes.table}
          aria-labelledby='tableTitle'
          size='medium'
          aria-label='enhanced table'
        >
          <EnhancedTableHead<T>
            order={order}
            headCells={headCells}
            orderBy={orderBy}
            onRequestSort={handleRequestSort}
            rowCount={itemsCount}
            allowSort={allowSort}
            onSelectAllClick={onSelectAllClick}
            data={data}
            numSelected={numSelected}
          />
          <TableBody>{body}</TableBody>
        </Table>
      </TableContainer>
      <TablePagination
        rowsPerPageOptions={rowsPerPageOptions}
        component='div'
        count={itemsCount}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
        backIconButtonProps={{ ...(loading && { disabled: true }) }}
        nextIconButtonProps={{ ...(loading && { disabled: true }) }}
      />
    </>
  );

  return (
    <div className={classes.root}>
      {isOnPaper ? <Paper className={classes.paper}>{table}</Paper> : table}
    </div>
  );
}
