import { type NextPage } from "next";
import Head from "next/head";
import Link from "next/link";
import Image from "next/image";
import { Fragment } from "react";
// import { Popover, Transition } from '@headlessui/react'
// import { MenuIcon, XIcon } from '@heroicons/react/outline'
import { ArrowSmallRightIcon } from "@heroicons/react/20/solid";

const Home: NextPage = () => {
  return (
    <>
      <Head>
        <title>Расписание РТУ МИРЭА</title>
        <meta name="description" content="Расписание РТУ МИРЭА" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <div className="flex min-h-screen flex-col items-center justify-center bg-gray-100 py-2">
        <main className="flex flex-col items-center justify-center w-full flex-1 px-20 text-center">
          <h1 className="text-6xl font-bold">Расписание РТУ МИРЭА</h1>
          <p className="mt-3 text-2xl">
            Поиск расписания на любой день недели
          </p>
          <div className="flex flex-wrap items-center justify-around max-w-4xl mt-6 sm:w-full">
            <a
              href="https://nextjs.org/docs"
              className="p-6 mt-6 text-left border w-96 rounded-xl hover:text-blue-600 focus:text-blue-600"
            >
              <h3 className="text-2xl font-bold">
                Поиск расписания по группе &rarr;
              </h3>
              <p className="mt-4 text-xl">
                Введите название группы, например: ИВТ-301
              </p>
            </a>

            <a
              href="https://nextjs.org/learn"
              className="p-6 mt-6 text-left border w-96 rounded-xl hover:text-blue-600 focus:text-blue-600"
            >
              <h3 className="text-2xl font-bold">
                Поиск расписания по преподавателю &rarr;
              </h3>
              <p className="mt-4 text-xl">
                Введите ФИО преподавателя, например: Иванов Иван Иванович
              </p>
            </a>
          </div>
        </main>
        
   
        <footer className="flex h-24 w-full items-center justify-center border-t">
          <a
            className="flex items-center justify-center"
            href="https://mirea.ninja"
            target="_blank"
            rel="noopener noreferrer"
          >
            Powered by
            <Image
              src="https://cdn2.mirea.ninja/original/2X/7/78bcc63aff95d9ad39e6a4de12937f45c97c8cb5.svg"
              alt="Mirea Ninja Logo"
              width={64}
              height={24}
              className="ml-2 h-6"
            />
            Mirea NInja
          </a>
        </footer>
      </div>
    </>
  );
};

export default Home;
