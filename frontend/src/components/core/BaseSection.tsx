import { Box, Paper, Typography } from '@material-ui/core';
import styled from 'styled-components';
import React, { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';

const PaperContainer = styled(Paper)`
  display: flex;
  padding: ${({ theme }) => theme.spacing(3)}px
    ${({ theme }) => theme.spacing(4)}px;
  margin: ${({ theme }) => theme.spacing(5)}px;
  flex-direction: column;
  border-bottom: 1px solid rgba(224, 224, 224, 1);
`;

interface BaseSectionProps {
  children: ReactElement;
  buttons?: ReactElement;
  title: string;
}

export const BaseSection = ({
  children,
  buttons,
  title,
}: BaseSectionProps): React.ReactElement => {
  const { t } = useTranslation();

  return (
    <PaperContainer>
      <Box display='flex' justifyContent='space-between'>
        <Typography variant='h6'>{t(title)}</Typography>
        {buttons}
      </Box>
      {children}
    </PaperContainer>
  );
};
