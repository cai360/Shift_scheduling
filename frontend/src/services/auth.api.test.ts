import MockAdapter from 'axios-mock-adapter';
import { describe, expect, it } from 'vitest';
import { createCompany, getMe, joinCompany, login, register } from './auth.api';
import http from '../utils/http';

const mock = new MockAdapter(http);

describe('auth api', () => {
  afterEach(() => {
    mock.reset();
  });

  it('logs in through the backend auth endpoint', async () => {
    mock.onPost('/auth/login').reply(200, {
      success: true,
      data: {
        access_token: 'access-token',
        refresh_token: 'refresh-token',
      },
    });

    const result = await login({
      email: 'test@example.com',
      password: 'password001',
    });

    expect(result).toEqual({
      success: true,
      data: {
        access_token: 'access-token',
        refresh_token: 'refresh-token',
      },
    });
  });

  it('registers a user', async () => {
    mock.onPost('/auth/register').reply(201, {
      success: true,
      data: {
        id: '6b9e66af-a799-460a-a421-b842a0368d8b',
        username: 'newuser',
        email: 'new@example.com',
      },
    });

    const result = await register({
      username: 'newuser',
      email: 'new@example.com',
      password: 'password001',
    });

    expect(result.data.email).toBe('new@example.com');
  });

  it('gets the current user with bearer token', async () => {
    localStorage.setItem('access_token', 'access-token');
    mock.onGet('/auth/me').reply(() => [
      200,
      {
        success: true,
        data: {
          id: '6b9e66af-a799-460a-a421-b842a0368d8b',
          username: 'testuser',
          email: 'test@example.com',
        },
      },
    ]);

    const result = await getMe();

    expect(result.data.email).toBe('test@example.com');
    expect(mock.history.get[0].headers?.Authorization).toBe(
      'Bearer access-token',
    );
  });

  it('creates and joins companies', async () => {
    mock.onPost('/companies').reply(201, {
      success: true,
      data: {
        id: '693991fa-6778-46e3-889b-cbc6fd5efeab',
        name: 'Shift Test Co',
        is_active: true,
        description: 'API test company',
      },
    });
    mock.onPost('/companies/company-1/join').reply(201, {
      success: true,
      data: {
        company_id: 'company-1',
        user_id: 'user-1',
        role: 'employee',
      },
    });

    await expect(
      createCompany({
        name: 'Shift Test Co',
        description: 'API test company',
      }),
    ).resolves.toMatchObject({
      data: { name: 'Shift Test Co' },
    });
    await expect(joinCompany('company-1')).resolves.toMatchObject({
      data: { role: 'employee' },
    });
  });
});
