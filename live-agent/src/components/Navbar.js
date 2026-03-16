import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ChevronDown, Menu, X } from 'lucide-react';
export default function Navbar() {
    const [isOpen, setIsOpen] = useState(false);
    const [scrolled, setScrolled] = useState(false);
    useEffect(() => {
        const handleScroll = () => setScrolled(window.scrollY > 20);
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);
    const navLinks = [
        { name: 'Home', path: '/' },
        { name: 'Services', path: '#', hasDropdown: true },
        { name: 'Reviews', path: '#' },
        { name: 'Contact us', path: '#' },
    ];
    return (_jsxs("nav", { className: `fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${scrolled ? 'bg-black/60 backdrop-blur-xl border-b border-white/5' : 'bg-transparent'}`, children: [_jsxs("div", { className: "max-w-[1440px] mx-auto px-6 md:px-[120px] h-[102px] flex items-center justify-between", children: [_jsxs("div", { className: "flex items-center", children: [_jsxs(Link, { to: "/", className: "flex items-center mr-[80px]", children: [_jsx("span", { className: "text-white font-black text-2xl tracking-tighter", children: "SYNAPSE" }), _jsx("div", { className: "w-1.5 h-1.5 rounded-full bg-primary-purple ml-1 animate-pulse" })] }), _jsx("div", { className: "hidden lg:flex items-center gap-[10px]", children: navLinks.map((link) => (_jsxs(Link, { to: link.path, className: "px-[10px] py-[4px] font-manrope font-medium text-[14px] leading-[22px] text-white hover:text-primary-purple transition-colors flex items-center gap-[3px]", children: [link.name, link.hasDropdown && _jsx(ChevronDown, { size: 14, className: "opacity-60" })] }, link.name))) })] }), _jsxs("div", { className: "hidden md:flex items-center gap-[12px]", children: [_jsx("button", { className: "px-[16px] py-[8px] bg-white border border-[#d4d4d4] rounded-[8px] font-manrope font-semibold text-[14px] leading-[22px] text-[#171717] hover:bg-white/90 transition-all", children: "Sign In" }), _jsx("button", { className: "px-[16px] py-[8px] bg-primary-purple rounded-[8px] font-manrope font-semibold text-[14px] leading-[22px] text-[#fafafa] shadow-[0px_4px_16px_rgba(23,23,23,0.04)] hover:bg-primary-purple-hover transition-all", children: "Get Started" })] }), _jsx("div", { className: "lg:hidden", children: _jsx("button", { onClick: () => setIsOpen(!isOpen), className: "text-white", children: isOpen ? _jsx(X, { size: 28 }) : _jsx(Menu, { size: 28 }) }) })] }), isOpen && (_jsxs("div", { className: "lg:hidden absolute top-[102px] left-0 right-0 bg-black/95 backdrop-blur-2xl border-b border-white/10 p-6 flex flex-col gap-6 animate-fade-in", children: [navLinks.map((link) => (_jsx(Link, { to: link.path, className: "text-lg font-medium text-white/80", onClick: () => setIsOpen(false), children: link.name }, link.name))), _jsxs("div", { className: "flex flex-col gap-4 mt-4", children: [_jsx("button", { className: "w-full py-4 bg-white text-black font-bold rounded-xl", children: "Sign In" }), _jsx("button", { className: "w-full py-4 bg-primary-purple text-white font-bold rounded-xl", children: "Get Started" })] })] }))] }));
}
