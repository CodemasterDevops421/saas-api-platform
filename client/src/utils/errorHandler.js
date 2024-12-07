export class APIError extends Error {
  constructor(message, code, status) {
    super(message);
    this.code = code;
    this.status = status;
  }
}

export const handleApiError = (error) => {
  if (error.response) {
    const { data, status } = error.response;
    throw new APIError(
      data.error?.message || 'Request failed',
      data.error?.code,
      status
    );
  }
  throw new APIError('Network error', 'NETWORK_ERROR', 0);
};