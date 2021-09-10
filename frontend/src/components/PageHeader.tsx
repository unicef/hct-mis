import React from 'react';
import { Typography } from '@material-ui/core';
import styled from 'styled-components';
import { useHistory } from 'react-router-dom';
import ArrowBackRoundedIcon from '@material-ui/icons/ArrowBackRounded';
import { BreadCrumbs, BreadCrumbsItem } from './BreadCrumbs';
import { Flag } from './Flag';
import { FlagTooltip } from './FlagTooltip';
import { useTranslation } from 'react-i18next';

const Wrapper = styled.div`
  box-shadow: 0px 2px 4px -1px rgba(0, 0, 0, 0.2),
    0px 4px 5px 0px rgba(0, 0, 0, 0.14), 0px 1px 10px 0px rgba(0, 0, 0, 0.12);
  position: relative;
  width: 100%;
  background-color: #fff;
`;

const Container = styled.div`
  display: flex;
  align-items: center;
  padding: ${({ theme }) => theme.spacing(7)}px
    ${({ theme }) => theme.spacing(11)}px;
`;
const HeaderContainer = styled.div`
  flex: 1;
  display: flex;
  justify-content: space-between;
  margin-left: ${({ theme }) => theme.spacing(5)}px;
`;
const ActionsContainer = styled.div`
  display: flex;
  align-items: center;
`;
const BackButton = styled.div`
  cursor: pointer;
`;

const TabsWrapper = styled.div`
  margin: 0 0 0 ${({ theme }) => theme.spacing(5)}px;
`;

const TitleWrapper = styled.div`
  width: 60%;
  min-width: 600px;
  transform: translateY(-12px);
  label:first-child {
    font-size: ${({ theme }) => theme.spacing(6)}px;
  }
  input:first-child {
    font-size: ${({ theme }) => theme.spacing(6)}px;
  }
  div:first-child {
    margin: 0;
  }
`;

interface Props {
  title: string | React.ReactElement;
  children?: React.ReactElement;
  breadCrumbs?: BreadCrumbsItem[];
  tabs?: React.ReactElement;
  hasInputComponent?: boolean;
  withTriangle?: boolean;
  possibleMatch?: boolean;
  confirmedMatch?: boolean;
}

export function PageHeader({
  title,
  children,
  breadCrumbs = null,
  tabs = null,
  hasInputComponent,
  possibleMatch = false,
  withTriangle = false,
  confirmedMatch = false,
}: Props): React.ReactElement {
  const history = useHistory();
  const { t } = useTranslation();
  return (
    <Wrapper data-cy='page-header-container'>
      <Container>
        {breadCrumbs && breadCrumbs.length !== 0 ? (
          <BackButton
            onClick={() => history.push(breadCrumbs[breadCrumbs.length - 1].to)}
          >
            <ArrowBackRoundedIcon fontSize='large' />
          </BackButton>
        ) : null}
        <HeaderContainer>
          <div>
            {React.isValidElement(title) && hasInputComponent ? (
              <TitleWrapper>{title}</TitleWrapper>
            ) : (
              <>
                {breadCrumbs && <BreadCrumbs breadCrumbs={breadCrumbs} />}
                <Typography variant='h5'>
                  {title}{' '}
                  {withTriangle && (
                    <FlagTooltip message={t('Possible Duplicate')} />
                  )}{' '}
                  {(possibleMatch || confirmedMatch) && (
                    <Flag
                      message={t('Sanction List Confirmed Match')}
                      confirmed={confirmedMatch}
                    />
                  )}
                </Typography>
              </>
            )}
          </div>
          <ActionsContainer>{children || null}</ActionsContainer>
        </HeaderContainer>
      </Container>
      <TabsWrapper>{tabs}</TabsWrapper>
    </Wrapper>
  );
}
