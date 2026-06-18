import MockAdapter from 'axios-mock-adapter';
import { describe, expect, it } from 'vitest';
import { getMyCompanies } from './company.api';
import http from '../utils/http';

const mock = new MockAdapter(http);

describe('company api', () => {
  afterEach(() => {
    mock.reset();
  });

  it('lists companies for the current user', async () => {
    mock.onGet('/users/me/companies').reply(200, {
      success: true,
      data: [
        {
          company_id: 'company-1',
          company_name: 'Shift Test Co',
          role: 'owner',
        },
      ],
    });

    const result = await getMyCompanies();

    expect(result.data).toEqual([
      {
        company_id: 'company-1',
        company_name: 'Shift Test Co',
        role: 'owner',
      },
    ]);
  });
});
