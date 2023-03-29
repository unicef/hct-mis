import { Box, Button, makeStyles } from '@material-ui/core';
import MuiAppBar from '@material-ui/core/AppBar';
import IconButton from '@material-ui/core/IconButton';
import TextsmsIcon from '@material-ui/icons/Textsms';
import Toolbar from '@material-ui/core/Toolbar';
import MenuIcon from '@material-ui/icons/Menu';
import clsx from 'clsx';
import React from 'react';
import styled from 'styled-components';
import { BusinessAreaSelect } from '../../containers/BusinessAreaSelect';
import { UserProfileMenu } from '../../containers/UserProfileMenu';
import { MiśTheme } from '../../theme';
import { useCachedMe } from '../../hooks/useCachedMe';

const useStyles = makeStyles((theme: MiśTheme) => ({
  root: {
    display: 'flex',
  },
  toolbarIcon: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'flex-end',
    padding: '0 8px',
    ...theme.mixins.toolbar,
  },
  appBar: {
    zIndex: theme.zIndex.drawer + 1,
    backgroundColor: theme.palette.secondary.main,
    transition: theme.transitions.create(['width', 'margin'], {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
  },
  appBarShift: {
    marginLeft: theme.drawer.width,
    width: `calc(100% - ${theme.drawer.width}px)`,
    transition: theme.transitions.create(['width', 'margin'], {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.enteringScreen,
    }),
  },
  menuButton: {
    marginRight: 36,
  },
  menuButtonHidden: {
    display: 'none',
  },
  title: {
    flexGrow: 1,
  },
  appBarSpacer: theme.mixins.toolbar,
}));
const BusinessAreaContainer = styled.div`
  margin-left: ${({ theme }) => theme.spacing(11)}px;
`;
const StyledToolbar = styled(Toolbar)`
  display: flex;
  justify-content: space-between;
`;
const StyledLink = styled.a`
  text-decoration: none;
  color: #e3e6e7;
`;

export function AppBar({ open, handleDrawerOpen }): React.ReactElement {
  const { data: meData, loading: meLoading } = useCachedMe();
  const classes = useStyles({});
  const servicenow = `https://unicef.service-now.com/cc?id=sc_cat_item&sys_id=762ae3128747d91021cb670a0cbb35a7&HOPE - ${
    window.location.pathname.split('/')[2]
  }&Workspace: ${window.location.pathname.split('/')[1]} \n Url: ${
    window.location.href
  }`;
  if (meLoading) {
    return null;
  }
  return (
    <MuiAppBar
      position='absolute'
      className={clsx(classes.appBar, open && classes.appBarShift)}
    >
      <StyledToolbar>
        <Box ml={1}>
          <IconButton
            edge='start'
            color='inherit'
            aria-label='open drawer'
            onClick={handleDrawerOpen}
            className={clsx(
              classes.menuButton,
              open && classes.menuButtonHidden,
            )}
          >
            <MenuIcon />
          </IconButton>
        </Box>
        <BusinessAreaContainer data-cy='business-area-container'>
          <BusinessAreaSelect />
        </BusinessAreaContainer>
        <Box display='flex' justifyContent='flex-end'>
          <Button startIcon={<TextsmsIcon style={{ color: '#e3e6e7' }} />}>
            <StyledLink target='_blank' href={servicenow}>
              Support
            </StyledLink>
          </Button>
          <UserProfileMenu meData={meData} />
        </Box>
      </StyledToolbar>
    </MuiAppBar>
  );
}
