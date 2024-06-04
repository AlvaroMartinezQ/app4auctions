import axios, { AxiosError } from 'axios'

const HTTP = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_URL,
  timeout: 12000
})

HTTP.interceptors.response.use(
  response => response,
  // Error should be resolved not rejected!
  // If it's rejected the execution of the calling function ends.
  error => Promise.resolve(processError(error))
);

function processError(error: AxiosError) {
  // Return an object as:
  // statusCode
  const e = {
    statusCode: error.response?.status,
    errorData: error.response?.data,
    msg: `There was an error with the request. ${error}`,
  }
  return e;
}

export default HTTP
