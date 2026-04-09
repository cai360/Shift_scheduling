import styles from './CompanySwitcher.module.css';
import { useCompanyContext } from '../../contexts/useCompanyContext';
import type { MenuProps } from 'antd';
import { Button, Dropdown } from 'antd';

const CompanySwitcher = () => {
  const { companies, currentCompanyId, switchCompany } = useCompanyContext();
  const currCompany = companies.find(
    (company) => company.company_id === currentCompanyId,
  );

  const items: MenuProps['items'] = companies.map((company) => ({
    key: company.company_id,
    label: (
      <div className={styles.menuItem}>
        <span>{company?.company_name ?? '-'}</span>
        <span>{company?.role}</span>
      </div>
    ),
    disabled: company.company_id === currentCompanyId,
  }));

  const handleMenuClick: MenuProps['onClick'] = ({ key }) => {
    switchCompany(key);
  };

  return (
    <Dropdown
      menu={{
        items,
        onClick: handleMenuClick,
        selectedKeys: currentCompanyId ? [currentCompanyId] : [],
      }}
      placement="bottomRight"
      arrow
    >
      <Button className={styles.companyButton}>
        <div className={styles.companySwitcher}>
          <span>{currCompany?.company_name ?? '-'}</span>
          <span>{currCompany?.role}</span>
        </div>
      </Button>
    </Dropdown>
  );
};

export default CompanySwitcher;
