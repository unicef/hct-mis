import { makeStyles, Snackbar, SnackbarContent } from '@mui/material';
import CssBaseline from '@mui/material/CssBaseline';
import * as React from 'react';
import { Redirect, useLocation } from 'react-router-dom';
import styled from 'styled-components';
import {
  useAllBusinessAreasQuery,
  useAllProgramsForChoicesQuery,
} from '@generated/graphql';
import { AppBar } from '@components/core/AppBar';
import { Drawer } from '@components/core/Drawer/Drawer';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { MiśTheme } from '../../theme';

const Root = styled.div`
  display: flex;
`;
const MainContent = styled.div`
  flex-grow: 1;
  height: 100vh;
  overflow: auto;
`;

const useStyles = makeStyles((theme: MiśTheme) => ({
  appBarSpacer: theme.mixins.toolbar,
}));

export function BaseHomeRouter({ children }): React.ReactElement {
  const [open, setOpen] = React.useState(true);
  const { businessArea } = useBaseUrl();
  const classes = useStyles({});
  const location = useLocation();
  const snackBar = useSnackbar();
  const handleDrawerOpen = (): void => {
    setOpen(true);
  };
  const handleDrawerClose = (): void => {
    setOpen(false);
  };
  const { data: businessAreaData, loading: businessAreaLoading } =
    useAllBusinessAreasQuery({
      variables: {
        slug: businessArea,
      },
      fetchPolicy: 'cache-first',
    });

  const { data: programsData, loading: programsLoading } =
    useAllProgramsForChoicesQuery({
      variables: { businessArea, first: 100 },
      fetchPolicy: 'cache-first',
    });

  if (!businessAreaData) {
    return null;
  }

  if (businessAreaLoading) {
    return <LoadingComponent />;
  }

  if (!businessAreaData || !programsData) {
    return null;
  }

  if (businessAreaLoading || programsLoading) {
    return <LoadingComponent />;
  }
  const allBusinessAreasSlugs = businessAreaData.allBusinessAreas.edges.map(
    (el) => el.node.slug,
  );
  const isBusinessAreaValid = allBusinessAreasSlugs.includes(businessArea);

  if (!isBusinessAreaValid) {
    return <Redirect to="/" noThrow />;
  }

  return (
    <Root>
      <CssBaseline />
      <AppBar open={open} handleDrawerOpen={handleDrawerOpen} />
      <Drawer
        open={open}
        handleDrawerClose={handleDrawerClose}
        currentLocation={location.pathname}
        dataCy="side-nav"
      />
      <MainContent data-cy="main-content">
        <div className={classes.appBarSpacer} />
        {children}
      </MainContent>
      {snackBar.show && (
        <Snackbar
          open={snackBar.show}
          autoHideDuration={5000}
          onClose={() => snackBar.setShow(false)}
        >
          <SnackbarContent
            message={snackBar.message}
            data-cy={snackBar.dataCy}
          />
        </Snackbar>
      )}
    </Root>
  );
}
