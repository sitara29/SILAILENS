import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Analyze from './pages/Analyze'
import Results from './pages/Results'
import Collection from './pages/Collection'
import SignIn from './pages/SignIn'
import SignUp from './pages/SignUp'
import './index.css'

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/"           element={<Home />} />
        <Route path="/analyze"    element={<Analyze />} />
        <Route path="/results"    element={<Results />} />
        <Route path="/collection" element={<Collection />} />
        <Route path="/signin"     element={<SignIn />} />
        <Route path="/signup"     element={<SignUp />} />
      </Routes>
    </BrowserRouter>
  )
}