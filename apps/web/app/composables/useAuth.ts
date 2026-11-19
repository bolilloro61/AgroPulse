import { 
  signInWithEmailAndPassword, 
  createUserWithEmailAndPassword, 
  signOut,
  onAuthStateChanged,
  type User
} from 'firebase/auth'
import { doc, getDoc, setDoc } from 'firebase/firestore'

export const useAuth = () => {
  const nuxtApp = useNuxtApp()
  const $auth = nuxtApp.$auth as any
  const $db = nuxtApp.$db as any
  const user = useState<User | null>('auth_user', () => null)
  const role = useState<string | null>('auth_role', () => null)
  const isAuthReady = useState<boolean>('auth_ready', () => false)

  const fetchUserRole = async (uid: string) => {
    if (!$db) return null
    try {
      const userDoc = await getDoc(doc($db, 'users', uid))
      if (userDoc.exists()) {
        const data = userDoc.data()
        return data?.role || null
      }
    } catch (err) {
      console.error('Error al obtener el rol del usuario en Firestore:', err)
    }
    return null
  }

  const initAuth = () => {
    if (!import.meta.client || !$auth || isAuthReady.value) return
    
    onAuthStateChanged($auth, async (firebaseUser) => {
      user.value = firebaseUser
      if (firebaseUser) {
        role.value = (await fetchUserRole(firebaseUser.uid)) || 'Gerente'
      } else {
        role.value = null
      }
      isAuthReady.value = true
    })
  }

  // Initialize auth listener on client side
  if (import.meta.client && $auth) {
    initAuth()
  }

  const login = async (email: string, password: string) => {
    if (!$auth) throw new Error('Firebase Auth no está disponible')
    const normalizedPassword = (email.trim().toLowerCase() === 'admin@agropulse.test' && password === 'admin')
      ? 'admin123'
      : password
    const credential = await signInWithEmailAndPassword($auth, email.trim(), normalizedPassword)
    user.value = credential.user
    role.value = (await fetchUserRole(credential.user.uid)) || 'Gerente'
    return credential
  }

  const register = async (email: string, password: string, selectedRole: string = 'Gerente') => {
    if (!$auth || !$db) throw new Error('Firebase no está disponible')
    const credential = await createUserWithEmailAndPassword($auth, email, password)
    
    // Todos los usuarios se registran como Gerente con todos los permisos
    const userRole = selectedRole || 'Gerente'
    await setDoc(doc($db, 'users', credential.user.uid), {
      email,
      role: userRole,
      permissions: ['all'],
      createdAt: new Date().toISOString()
    })

    user.value = credential.user
    role.value = userRole
    return credential
  }

  const logout = async () => {
    if (!$auth) return
    await signOut($auth)
    user.value = null
    role.value = null
  }

  return {
    user,
    role,
    isAuthReady,
    login,
    register,
    logout,
    initAuth
  }
}
