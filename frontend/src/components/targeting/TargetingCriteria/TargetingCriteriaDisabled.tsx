import * as React from 'react';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import { Typography, Paper, Tooltip } from '@mui/material';
import { AddCircleOutline } from '@mui/icons-material';

const PaperContainer = styled(Paper)`
  padding: ${({ theme }) => theme.spacing(3)} ${({ theme }) => theme.spacing(4)};
  margin: ${({ theme }) => theme.spacing(5)};
  border-bottom: 1px solid rgba(224, 224, 224, 1);
`;

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(4)};
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const ContentWrapper = styled.div`
  display: flex;
  flex-wrap: wrap;
  padding: ${({ theme }) => theme.spacing(4)} 0;
`;

const IconWrapper = styled.div`
  display: flex;
  color: #a0b6d6;
`;

const AddCriteria = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  color: #003c8f;
  border: 2px solid #a0b6d6;
  border-radius: 3px;
  font-size: 16px;
  padding: ${({ theme }) => theme.spacing(6)}
    ${({ theme }) => theme.spacing(28)};
  cursor: pointer;
  p {
    font-weight: 500;
    margin: 0 0 0 ${({ theme }) => theme.spacing(2)};
  }
`;

export function TargetingCriteriaDisabled({
  showTooltip = false,
}): React.ReactElement {
  const { t } = useTranslation();
  return (
    <div>
      <PaperContainer>
        <Title>
          <Typography variant="h6">{t('Targeting Criteria')}</Typography>
        </Title>
        {showTooltip ? (
          <ContentWrapper>
            <Tooltip title="Make sure program has checked household filter flag or individual filter flag">
              <div>
                <AddCriteria
                  onClick={() => null}
                  data-cy="button-target-population-disabled-add-criteria"
                >
                  <IconWrapper>
                    <AddCircleOutline />
                    <p>{t('Add Filter')}</p>
                  </IconWrapper>
                </AddCriteria>
              </div>
            </Tooltip>
          </ContentWrapper>
        ) : (
          <ContentWrapper>
            <AddCriteria
              onClick={() => null}
              data-cy="button-target-population-disabled-add-criteria"
            >
              <IconWrapper>
                <AddCircleOutline />
                <p>{t('Add Filter')}</p>
              </IconWrapper>
            </AddCriteria>
          </ContentWrapper>
        )}
      </PaperContainer>
    </div>
  );
}
