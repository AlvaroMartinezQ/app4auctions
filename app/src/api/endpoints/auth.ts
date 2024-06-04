import CLIENT_API_IMP, { getCookie } from 'app/src/api/client.api';

type APIData = Record<string, any>;

type UserAuthOP = (data: APIData) => ReturnType<typeof CLIENT_API_IMP.post>
type UserData = () => ReturnType<typeof CLIENT_API_IMP.auth_get>
type UserActivate = (id: string) => ReturnType<typeof CLIENT_API_IMP.get>
type UpdateUserData = (email: string, data: APIData) => ReturnType<typeof CLIENT_API_IMP.auth_put>
type UpdateUserEmail = (data: APIData) => ReturnType<typeof CLIENT_API_IMP.auth_post>
type UpdateUserPassword = (data: APIData) => ReturnType<typeof CLIENT_API_IMP.auth_post>
type ResetUserPasswordEmail = (data: APIData) => ReturnType<typeof CLIENT_API_IMP.post>
type ResetUserPasswordToken = (data: APIData) => ReturnType<typeof CLIENT_API_IMP.post>

interface AUTH_API {
  login: UserAuthOP,
  getUserData: UserData,
  createUser: UserAuthOP,
  activateUser: UserActivate,
  updateUser: UpdateUserData,
  updateUserPassword: UpdateUserPassword,
  updateUserEmail: UpdateUserEmail,
  resetPasswordEmail: ResetUserPasswordEmail,
  resetPasswordToken: ResetUserPasswordToken,
}

const AUTH_API_IMP: AUTH_API = {
  login(data) {
    return CLIENT_API_IMP.post('/auth/user/login', data);
  },
  getUserData() {
    return CLIENT_API_IMP.auth_get('/auth/user/', getCookie('appforauctionsauth'));
  },
  createUser(data) {
    return CLIENT_API_IMP.post('/auth/user/', data);
  },
  activateUser(id) {
    return CLIENT_API_IMP.get(`/auth/user/activate/${id}/`)
  },
  updateUser(email, data) {
    return CLIENT_API_IMP.auth_put(`/auth/user/?previous_email=${email}`, data, getCookie('appforauctionsauth'));
  },
  updateUserPassword(data) {
    return CLIENT_API_IMP.auth_post('/auth/user/password-change/', data, getCookie('appforauctionsauth'));
  },
  updateUserEmail(data) {
    return CLIENT_API_IMP.auth_post('/auth/user/email-change/', data, getCookie('appforauctionsauth'));
  },
  resetPasswordEmail(data) {
    return CLIENT_API_IMP.post(`/auth/user/password-reset/?email=${data.email}`, {});
  },
  resetPasswordToken(data) {
    return CLIENT_API_IMP.post(`/auth/user/password-reset/?email=${data.email}&email_token=${data.token}&new_password=${data.password}`, {});
  }
}

export default AUTH_API_IMP