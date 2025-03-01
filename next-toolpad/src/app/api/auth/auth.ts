import NextAuth from 'next-auth';
import Credentials from 'next-auth/providers/credentials';
import type { Provider } from 'next-auth/providers';

import { login, token } from '../../../dejtnf-api/user';
const providers: Provider[] = [Credentials({

  credentials: {
    email: { label: 'Email Address', type: 'email' },
    password: { label: 'Password', type: 'password' },
  },
  async authorize(credentials) {
    try {
      const user_data = await login(credentials); // Ensure this is awaited

      if (!user_data || user_data.error) {
        console.error('Authorization failed:', user_data?.error);
        return null;
      }

      const user = {
        id: user_data.user._id,
        name: user_data.user.name,
        email: user_data.user.email,
        role: user_data.user.role,
        // token: user_data.token,
      };

      // console.log('Returned User:', user);
      return user;
    } catch (error) {
      console.error('Authorize Error:', error);
      return null;
    }
  },
}),
];

export const providerMap = providers.map((provider) => {
  if (typeof provider === 'function') {
    const providerData = provider();
    return { id: providerData.id, name: providerData.name };
  }
  return { id: provider.id, name: provider.name };
});

export const { handlers, auth, signIn, signOut } = NextAuth({
  providers,
  secret: process.env.AUTH_SECRET,
  pages: {
    signIn: '/auth/signin',
  },
  callbacks: {
    jwt({ token, user }) {
      if (user) token.role = user.role
      return token
    },
    session({ session, token }) {
      session.user.role = token.role
      return session
    }
  }
  // callbacks: {
  //   async session({ session, token }) {
  //     session.user.id = token.id;
  //     session.user.role = token.role;
  //     return session;
  //   },
  //   async jwt({ token, user }) {
  //     if (user) {
  //       token.id = user.id;
  //       token.role = user.role;
  //     }
  //     return token;
  //   },
  //   async authorized({ req, token }) {
  //     const isLoggedIn = !!token;
  //     const isPublicPage = req.nextUrl.pathname.startsWith('/public');

  //     if (isPublicPage || isLoggedIn) {
  //       return true;
  //     }

  //     return false; // Redirect unauthenticated users to login page
  //   },
  // },
  // callbacks: {
  //   authorized({ auth: session, request: { nextUrl } }) {
  //     const isLoggedIn = !!session?.user;
  //     const isPublicPage = nextUrl.pathname.startsWith('/public');

  //     if (isPublicPage || isLoggedIn) {
  //       return true;
  //     }

  //     return false; // Redirect unauthenticated users to login page
  //   },
  // },
});
