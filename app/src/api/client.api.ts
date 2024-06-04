import type { AxiosPromise, AxiosRequestConfig } from 'axios'
import HTTP from 'app/src/api/http.config'


export function getCookie(name: string) {
  // Method gets the requested cookie for auth
  // For nested routes cookie will be in the last index of the
  // parts variable, this is the reason of the `for` loop
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  for (const value of parts) {
    if (value !== '' && value !== null) {
      return value;
    }
  }
  // if (parts.length === 2) {
  //   return parts[1]
  // }
  return null;
}


interface CLIENT_API {
  // No required auth
  get: (url: string, conf?: AxiosRequestConfig | undefined) => AxiosPromise<any>,
  post: (url: string, data: Record<any, any>, conf?: AxiosRequestConfig | undefined) => AxiosPromise<any>,
  // Required auth
  auth_get: (url: string, token: string | undefined | null, conf?: AxiosRequestConfig | undefined) => AxiosPromise<any>,
  image_get: (url: string, conf?: AxiosRequestConfig | undefined) => AxiosPromise<any>,
  auth_post: (url: string, data: Record<any, any>, token: string | undefined | null, conf?: AxiosRequestConfig | undefined) => AxiosPromise<any>,
  image_post: (url: string, data: any, token: string | undefined | null, conf?: AxiosRequestConfig | undefined) => AxiosPromise<any>,
  auth_put: (url: string, data: Record<any, any>, token: string | undefined | null, conf?: AxiosRequestConfig | undefined) => AxiosPromise<any>,
  // Required auth - no data
  e_auth_post: (url: string, token: string | undefined | null, conf?: AxiosRequestConfig | undefined) => AxiosPromise<any>,
  e_auth_put: (url: string, token: string | undefined | null, conf?: AxiosRequestConfig | undefined) => AxiosPromise<any>,
}

const CLIENT_API_IMP: CLIENT_API = {
  get: function (url: string, conf?: AxiosRequestConfig): AxiosPromise<any> {
    return HTTP.get(url,
      {
        ...conf,
        headers: {
          ...conf?.headers,
          Accept: 'image/png',
        },
      }
    );
  },
  image_get: function (url: string, conf?: AxiosRequestConfig): AxiosPromise<any> {
    return HTTP.get(url, conf);
  },
  post: function (url: string, data: Record<any, any>, conf?: AxiosRequestConfig | undefined): AxiosPromise<any> {
    return HTTP.post(url,
      data,
      {
        ...conf,
        headers: {
          ...conf?.headers,
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
      }
    );
  },
  auth_get: function (url: string, token, conf?: AxiosRequestConfig): AxiosPromise<any> {
    return HTTP.get(
      url,
      {
        ...conf,
        headers: {
          ...conf?.headers,
          Authorization: `Bearer ${token}`
        },
        withCredentials: true
      }
    );
  },
  auth_post: function (url: string, data: Record<any, any>, token: string | null | undefined, conf?: AxiosRequestConfig): AxiosPromise<any> {
    return HTTP.post(url,
      data,
      {
        ...conf,
        headers: {
          ...conf?.headers,
          'Content-Type': 'application/json',
          Accept: 'application/json',
          Authorization: `Bearer ${token}`
        },
        withCredentials: true
      }
    );
  },
  image_post: function (url: string, data: any, token: string | null | undefined, conf?: AxiosRequestConfig): AxiosPromise<any> {
    return HTTP.post(url,
      data,
      {
        ...conf,
        headers: {
          ...conf?.headers,
          // 'Content-Type': 'multipart/form-data',
          Accept: 'multipart/form-data',
          Authorization: `Bearer ${token}`
        },
        withCredentials: true
      }
    );
  },
  auth_put: function (url: string, data: Record<any, any>, token: string | null | undefined, conf?: AxiosRequestConfig): AxiosPromise<any> {
    return HTTP.put(url,
      data,
      {
        ...conf,
        headers: {
          ...conf?.headers,
          'Content-Type': 'application/json',
          Accept: 'application/json',
          Authorization: `Bearer ${token}`
        },
        withCredentials: true
      }
    );
  },
  e_auth_post: function (url: string, token: string | null | undefined, conf?: AxiosRequestConfig): AxiosPromise<any> {
    return HTTP.post(url,
      {},
      {
        ...conf,
        headers: {
          ...conf?.headers,
          'Content-Type': 'application/json',
          Accept: 'application/json',
          Authorization: `Bearer ${token}`
        },
        withCredentials: true
      }
    );
  },
  e_auth_put: function (url: string, token: string | null | undefined, conf?: AxiosRequestConfig): AxiosPromise<any> {
    return HTTP.put(url,
      {},
      {
        ...conf,
        headers: {
          ...conf?.headers,
          'Content-Type': 'application/json',
          Accept: 'application/json',
          Authorization: `Bearer ${token}`
        },
        withCredentials: true
      }
    );
  }
}

export default CLIENT_API_IMP
