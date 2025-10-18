export interface Result<T> {
    resultCode: number;
    message?: string;
    data: T;
}