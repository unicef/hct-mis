import { Box, Button } from '@material-ui/core';
import { Refresh } from '@material-ui/icons';
import DashboardIcon from '@material-ui/icons/Dashboard';
import ArrowBackIcon from '@material-ui/icons/ArrowBack';
import React from 'react';
import { Link, useHistory } from 'react-router-dom';
import styled from 'styled-components';
import { getClient } from '../../../apollo/client';
import { clearCache } from '../../../utils/utils';
import SomethingWentWrongGraphic from './something_went_wrong_graphic.png';
import HopeLogo from './something_went_wrong_hope_logo.png';

const Container = styled.div`
  background-color: #ffffff;
  text-align: center;
  padding-top: 150px;
  font-family: 'Roboto', sans-serif;
  height: 100vh;
`;

const LogoContainer = styled.div`
  position: absolute;
  top: 20px;
  left: 20px;
`;

const SquareLogo = styled.div`
  display: inline-block;
  background-color: white;
  padding: 20px;
  margin-bottom: 20px;
`;

const TextContainer = styled.div`
  max-width: 450px;
  text-align: center;
  margin: 0 auto;
`;

const Title = styled.h1`
  font-size: 32px;
  font-weight: lighter;
  color: #233944;
  line-height: 32px;
`;

const Paragraph = styled.p`
  font-size: 24px;
  color: #666666;
  line-height: 32px;
`;

export const SomethingWentWrong: React.FC = () => {
  const goBackAndClearCache = async (): Promise<void> => {
    const client = await getClient();
    await clearCache(client);
    window.history.back();
  };
  const history = useHistory();
  const pathSegments = history.location.pathname.split('/');
  const businessArea = pathSegments[2];
  const errorMessage = history.location.state?.errorMessage;
  const shouldGoBack = history.location.state?.shouldGoBack;

  const handleGoBack = (): void => {
    if (window.history.length > 2) {
      window.history.go(-2);
    } else {
      window.history.back();
    }
  };

  return (
    <Container>
      <LogoContainer>
        <img src={HopeLogo} alt='Hope Logo' width='186' height='101' />
      </LogoContainer>
      <SquareLogo>
        <img
          src={SomethingWentWrongGraphic}
          alt='Sad face'
          width='354'
          height='293'
        />
      </SquareLogo>
      <TextContainer>
        <Title>Oops! Something went wrong</Title>
        {errorMessage ? (
          <Paragraph>{errorMessage}</Paragraph>
        ) : (
          <Paragraph>
            Don&apos;t worry! Our team is on it, working to fix the issue.
            Please try again later. Thank you for your patience.
          </Paragraph>
        )}
      </TextContainer>
      <Box display='flex' justifyContent='center' alignItems='center'>
        <Box mr={4}>
          <Button
            endIcon={<Refresh />}
            variant='outlined'
            color='primary'
            data-cy='button-refresh-page'
            onClick={goBackAndClearCache}
          >
            REFRESH PAGE
          </Button>
        </Box>
        {shouldGoBack === 'true' ? (
          <Button
            endIcon={<ArrowBackIcon />}
            color='primary'
            variant='contained'
            onClick={handleGoBack}
            data-cy='button-go-back'
          >
            GO BACK
          </Button>
        ) : (
          businessArea && (
            <Button
              endIcon={<DashboardIcon />}
              color='primary'
              variant='contained'
              component={Link}
              data-cy='button-go-to-country-dashboard'
              to={`/${businessArea}/programs/all/country-dashboard`}
            >
              GO TO COUNTRY DASHBOARD
            </Button>
          )
        )}
      </Box>
    </Container>
  );
};
