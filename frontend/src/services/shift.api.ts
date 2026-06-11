import http from '../utils/http';

export type ShiftStatus = 'draft' | 'published';

export interface Shift {
  id: string;
  company_id: string;
  start_at: string;
  end_at: string;
  capacity: number;

  published_at: string | null;
  deleted_at: string | null;
  created_at: string;
  updated_at: string;

  status: ShiftStatus;
  assignment_count: number;
  remaining_capacity: number;
}

export interface ShiftQueryParams {
  status?: ShiftStatus;
  from?: string;
  to?: string;
}

export type ShiftsResponse = Shift[];

export const getShifts = async (
  companyId: string,
  params?: ShiftQueryParams,
): Promise<ShiftsResponse> => {
  const response = await http.get<ShiftsResponse>(
    `/companies/${companyId}/shifts`,
    { params },
  );
  return response.data;
};
